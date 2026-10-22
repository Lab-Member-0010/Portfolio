from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import DB, CurrentAdmin
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AdminUser
from app.services import ratelimit
from app.schemas.auth import AdminOut, ChangePasswordRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_LIMIT, LOGIN_WINDOW = 10, 900  # 10 failed attempts / 15 min / IP


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: DB):
    key = f"login:{ratelimit.client_ip(request)}"
    ratelimit.check(db, key, LOGIN_LIMIT, LOGIN_WINDOW, "Too many failed sign-ins — try again in 15 minutes")
    user = db.scalar(select(AdminUser).where(AdminUser.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        ratelimit.record(db, key)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    ratelimit.clear(db, key)
    token, expires = create_access_token(user.email)
    return TokenResponse(access_token=token, expires_in=expires)


@router.get("/me", response_model=AdminOut)
def me(admin: CurrentAdmin):
    return AdminOut(id=admin.id, email=admin.email)


@router.post("/change-password", status_code=204)
def change_password(body: ChangePasswordRequest, admin: CurrentAdmin, db: DB):
    if not verify_password(body.current_password, admin.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    admin.password_hash = hash_password(body.new_password)
    db.add(admin)
    db.commit()
