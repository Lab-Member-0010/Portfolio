from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


def create_access_token(subject: str) -> tuple[str, int]:
    s = get_settings()
    expires = timedelta(minutes=s.jwt_expire_minutes)
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + expires, "type": "access"}
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm), int(expires.total_seconds())


def decode_token(token: str) -> str | None:
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    return payload.get("sub") if payload.get("type") == "access" else None
