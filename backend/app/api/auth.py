from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_token_expiry,
    generate_reset_token,
    hash_reset_token,
    reset_token_expiry,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def _issue_tokens(db: Session, user: User) -> dict:
    access_token = create_access_token(data={"sub": str(user.id)})
    plaintext_refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(plaintext_refresh),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": plaintext_refresh,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


@router.post("/register")
@limiter.limit("3/hour")
def register(request: Request, user_data: RegisterRequest, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    existing_email = db.query(User).filter(User.email == user_data.email).first()

    # Specific messages here are fine — registration is inherently
    # revealing usernames/emails are taken (that's the whole point of
    # the uniqueness check), unlike login where we're choosing to be
    # specific below as a deliberate, documented trade-off for this
    # project's scope (see note on /login).
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken.",
        )
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user_data: LoginRequest, db: Session = Depends(get_db)):
    """
    NOTE ON SECURITY TRADE-OFF: this deliberately returns SPECIFIC error
    messages ("no account with this email" vs "incorrect password")
    rather than a single generic "invalid email or password" message.

    The generic version is standard practice to prevent user
    enumeration (an attacker discovering which emails are registered by
    trying many and watching which ones say "wrong password" instead of
    "no such account"). For a small personal project this risk is low
    and the specific messages are meaningfully better UX. If this app
    is ever opened up to untrusted/public registration at scale, revert
    this to a single generic message.
    """
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found with that email address.",
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    tokens = _issue_tokens(db, user)
    return {"message": "Login successful", **tokens}


@router.post("/refresh")
@limiter.limit("20/minute")
def refresh(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not stored or stored.revoked_at is not None or _aware(stored.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == stored.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    stored.revoked_at = datetime.now(timezone.utc)
    db.commit()

    tokens = _issue_tokens(db, user)
    return {"message": "Token refreshed", **tokens}


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return {"message": "Logged out"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}


@router.post("/forgot-password")
@limiter.limit("3/hour")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    reset_link = None
    if user:
        plaintext_token = generate_reset_token()
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_reset_token(plaintext_token),
                expires_at=reset_token_expiry(),
            )
        )
        db.commit()
        reset_link = f"{settings.frontend_url}/reset-password?token={plaintext_token}"

        print("=" * 60)
        print("PASSWORD RESET REQUESTED")
        print(f"For: {user.email}")
        print(f"Link: {reset_link}")
        print("=" * 60)
    else:
        # Login already reveals whether an email is registered, so being
        # specific here too is consistent rather than a new leak.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with that email address.",
        )

    return {
        "message": "A password reset link has been generated.",
        "reset_link": reset_link,
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_reset_token(payload.token)
    stored = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )

    if not stored or stored.used_at is not None:
        raise HTTPException(status_code=400, detail="This reset link has already been used or is invalid.")

    if _aware(stored.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This reset link has expired. Please request a new one.")

    user = db.query(User).filter(User.id == stored.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="This reset link is invalid.")

    user.hashed_password = hash_password(payload.new_password)
    stored.used_at = datetime.now(timezone.utc)

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})

    db.commit()

    return {"message": "Your password has been reset. Please log in with your new password."}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Your current password is incorrect.")

    current_user.hashed_password = hash_password(payload.new_password)

    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id, RefreshToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})

    db.commit()

    return {"message": "Password changed successfully."}