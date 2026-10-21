from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import AdminUser

bearer = HTTPBearer(auto_error=False)
DB = Annotated[Session, Depends(get_db)]


def get_current_admin(
    db: DB, creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
) -> AdminUser:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
    )
    if creds is None:
        raise unauthorized
    email = decode_token(creds.credentials)
    if not email:
        raise unauthorized
    user = db.scalar(select(AdminUser).where(AdminUser.email == email))
    if user is None:
        raise unauthorized
    return user


CurrentAdmin = Annotated[AdminUser, Depends(get_current_admin)]
