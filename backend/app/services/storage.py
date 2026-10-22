"""File storage for PDFs (résumé, certificates).

* Local disk (default): files under UPLOAD_DIR; the stored reference is the relative path,
  e.g. "resume.pdf" or "certificates/3-aws.pdf".
* Vercel Blob (when BLOB_READ_WRITE_TOKEN is set): the stored reference is the public blob URL.

Callers only ever see references, so switching backends needs no other code changes.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse, Response

from app.core.config import get_settings

BLOB_API = "https://vercel.com/api/blob"
BLOB_API_VERSION = "13"


def is_url(ref: str) -> bool:
    return ref.startswith("https://") or ref.startswith("http://")


class LocalStorage:
    name = "local"

    def __init__(self, root: Path):
        self.root = root

    def _path(self, ref: str) -> Path:
        path = (self.root / ref).resolve()
        if self.root.resolve() not in path.parents:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid file reference")
        return path

    def save(self, key: str, data: bytes, content_type: str = "application/pdf") -> str:
        path = self._path(key)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(path)
        except OSError as exc:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "No writable storage — on Vercel, connect a Blob store to this project.",
            ) from exc
        return key

    def delete(self, ref: str) -> None:
        if ref and not is_url(ref):
            try:
                self._path(ref).unlink(missing_ok=True)
            except OSError:
                pass

    def exists(self, ref: str) -> bool:
        return bool(ref) and not is_url(ref) and self._path(ref).is_file()

    def size(self, ref: str) -> int | None:
        return self._path(ref).stat().st_size if self.exists(ref) else None

    def response(self, ref: str, filename: str, inline: bool) -> Response:
        if not self.exists(ref):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
        return FileResponse(
            self._path(ref), media_type="application/pdf", filename=filename,
            content_disposition_type="inline" if inline else "attachment",
        )


class BlobStorage:
    """Minimal Vercel Blob client (same REST calls as the official @vercel/blob SDK)."""

    name = "vercel-blob"

    def __init__(self, token: str, transport: httpx.BaseTransport | None = None):
        self.token = token
        parts = token.split("_")
        self.store_id = parts[3] if len(parts) > 3 else ""
        self.client = httpx.Client(timeout=30, transport=transport)

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        return {
            "authorization": f"Bearer {self.token}",
            "x-api-version": BLOB_API_VERSION,
            "x-vercel-blob-store-id": self.store_id,
            "x-api-blob-request-id": f"{self.store_id}:{uuid.uuid4().hex}",
            "x-api-blob-request-attempt": "0",
            **(extra or {}),
        }

    @staticmethod
    def _raise(res: httpx.Response) -> None:
        if res.is_success:
            return
        try:
            message = res.json().get("error", {}).get("message") or res.text
        except ValueError:
            message = res.text
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Blob storage error ({res.status_code}): {message[:200]}")

    def save(self, key: str, data: bytes, content_type: str = "application/pdf") -> str:
        res = self.client.put(
            f"{BLOB_API}/?{urlencode({'pathname': key})}",
            content=data,
            headers=self._headers({
                "x-vercel-blob-access": "public",
                "x-content-type": content_type,
                # unique URL per upload, so CDN caches never serve an old version
                "x-add-random-suffix": "1",
                "x-content-length": str(len(data)),
            }),
        )
        self._raise(res)
        return res.json()["url"]

    def delete(self, ref: str) -> None:
        if not ref or not is_url(ref):
            return
        try:
            res = self.client.post(
                f"{BLOB_API}/delete", json={"urls": [ref]},
                headers=self._headers({"content-type": "application/json"}),
            )
            self._raise(res)
        except (httpx.HTTPError, HTTPException):
            pass  # an orphaned file is harmless; never block the user's action on cleanup

    def exists(self, ref: str) -> bool:
        return is_url(ref)

    def size(self, ref: str) -> int | None:
        return None

    def response(self, ref: str, filename: str, inline: bool) -> Response:
        if not is_url(ref):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")
        url = ref if inline else f"{ref}?{urlencode({'download': '1'})}"
        return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


_storage: LocalStorage | BlobStorage | None = None


def get_storage() -> LocalStorage | BlobStorage:
    global _storage
    if _storage is None:
        s = get_settings()
        _storage = BlobStorage(s.blob_read_write_token) if s.use_blob_storage else LocalStorage(s.upload_path)
    return _storage


def set_storage(storage: LocalStorage | BlobStorage | None) -> None:
    """Testing hook."""
    global _storage
    _storage = storage


def storage_for(ref: str) -> LocalStorage | BlobStorage:
    """Whichever backend can serve/delete this reference (handles refs created before a switch)."""
    current = get_storage()
    if is_url(ref) or isinstance(current, LocalStorage):
        return current
    return LocalStorage(get_settings().upload_path)
