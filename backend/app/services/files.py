"""Certificate PDFs live in uploads/certificates/."""
import re
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings


def certificates_dir() -> Path:
    path = get_settings().upload_path / "certificates"
    path.mkdir(parents=True, exist_ok=True)
    return path


async def read_pdf_upload(file: UploadFile) -> bytes:
    limit = get_settings().max_resume_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File too large")
    if not data.startswith(b"%PDF"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Please upload a PDF file")
    return data


def safe_name(item_id: int, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "certificate"
    return f"{item_id}-{slug}.pdf"
