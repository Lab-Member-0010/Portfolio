from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DB, CurrentAdmin
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AdminUser
from app.schemas.auth import AdminOut, ChangePasswordRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DB):
    user = db.scalar(select(AdminUser).where(AdminUser.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
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
