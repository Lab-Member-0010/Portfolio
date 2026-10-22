"""Database-backed rate limiting, so limits hold across serverless instances and workers."""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import RateEvent


def client_ip(request: Request) -> str:
    """Real visitor IP. Behind Vercel (or a trusted proxy) the first x-forwarded-for entry is the
    client; otherwise use the socket peer (uvicorn already applies --proxy-headers for localhost)."""
    s = get_settings()
    if s.on_vercel or s.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real = request.headers.get("x-real-ip")
        if real:
            return real.strip()
    return request.client.host if request.client else "unknown"


def _since(window_seconds: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=window_seconds)


def check(db: Session, key: str, limit: int, window_seconds: int, message: str) -> None:
    """Raise 429 if `key` already has `limit` events inside the window."""
    db.execute(delete(RateEvent).where(RateEvent.created_at < _since(max(window_seconds, 3600))))
    count = db.scalar(
        select(func.count(RateEvent.id)).where(RateEvent.key == key, RateEvent.created_at >= _since(window_seconds))
    )
    db.commit()
    if (count or 0) >= limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, message)


def record(db: Session, key: str) -> None:
    db.add(RateEvent(key=key))
    db.commit()


def clear(db: Session, key: str) -> None:
    db.execute(delete(RateEvent).where(RateEvent.key == key))
    db.commit()
