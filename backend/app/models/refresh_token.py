import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RefreshToken(Base):
    """
    A refresh token is stored HASHED (never plaintext — same principle as
    passwords), so that a database leak alone can't be used to impersonate
    users. The plaintext token is only ever returned to the client once,
    at issuance.

    Revocable: logout (or a future "sign out all devices" feature) sets
    revoked_at, which immediately invalidates it server-side even though
    the JWT-based access token it minted may still be technically valid
    for a few more minutes.
    """

    __tablename__ = "refresh_tokens"

    id = Column(String(32), primary_key=True, default=_new_id, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=_utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="refresh_tokens")