"""The résumé PDF: its storage reference + metadata live in app_meta."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AppMeta
from app.services.storage import get_storage, storage_for

REF_KEY, SIZE_KEY, UPDATED_KEY = "resume_ref", "resume_size", "resume_updated_at"
DEFAULT_LOCAL_REF = "resume.pdf"


def _get(db: Session, key: str) -> str:
    row = db.get(AppMeta, key)
    return row.value if row else ""


def _set(db: Session, key: str, value: str) -> None:
    row = db.get(AppMeta, key)
    if row is None:
        db.add(AppMeta(key=key, value=value))
    else:
        row.value = value


def resume_ref(db: Session) -> str:
    return _get(db, REF_KEY)


def resume_info(db: Session) -> dict:
    ref = resume_ref(db)
    if not ref or not storage_for(ref).exists(ref):
        return {"available": False}
    size = _get(db, SIZE_KEY) or storage_for(ref).size(ref)
    return {
        "available": True,
        "size": int(size) if size else None,
        "updated_at": _get(db, UPDATED_KEY) or None,
    }


def save_resume(db: Session, data: bytes) -> dict:
    old = resume_ref(db)
    new = get_storage().save("resume/resume.pdf" if get_storage().name != "local" else DEFAULT_LOCAL_REF, data)
    if old and old != new:
        storage_for(old).delete(old)
    _set(db, REF_KEY, new)
    _set(db, SIZE_KEY, str(len(data)))
    _set(db, UPDATED_KEY, datetime.now(timezone.utc).isoformat())
    db.commit()
    return resume_info(db)


def delete_resume(db: Session) -> None:
    ref = resume_ref(db)
    if ref:
        storage_for(ref).delete(ref)
    for key in (REF_KEY, SIZE_KEY, UPDATED_KEY):
        _set(db, key, "")
    db.commit()
