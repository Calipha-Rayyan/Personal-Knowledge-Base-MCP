import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if "sub" not in payload:
            raise JWTError("Token does not contain user ID")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------------------------------------------------------------
# Opaque, hashed tokens (refresh tokens + password reset tokens share
# this same pattern: random string, SHA-256 hash stored, plaintext
# handed to the client exactly once).
# ---------------------------------------------------------------------

def _generate_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def _hash_opaque_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> str:
    return _generate_opaque_token()


def hash_refresh_token(token: str) -> str:
    return _hash_opaque_token(token)


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)


def generate_reset_token() -> str:
    return _generate_opaque_token()


def hash_reset_token(token: str) -> str:
    return _hash_opaque_token(token)


def reset_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.reset_token_expire_minutes)