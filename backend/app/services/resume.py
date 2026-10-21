from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings

RESUME_NAME = "resume.pdf"


def resume_path() -> Path:
    return get_settings().upload_path / RESUME_NAME


def resume_info() -> dict:
    p = resume_path()
    if not p.exists():
        return {"available": False}
    st = p.stat()
    return {
        "available": True,
        "size": st.st_size,
        "updated_at": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
    }
