"""Upload validation + naming for PDFs."""
import re

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings


async def read_pdf_upload(file: UploadFile) -> bytes:
    limit = get_settings().max_resume_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f"File too large (max {get_settings().max_resume_mb} MB)")
    if not data.startswith(b"%PDF"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Please upload a PDF file")
    return data


def certificate_key(item_id: int, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "certificate"
    return f"certificates/{item_id}-{slug}.pdf"
