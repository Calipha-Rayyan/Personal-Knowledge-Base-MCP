import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PasswordResetToken(Base):
    """
    Stored hashed (same reasoning as passwords and refresh tokens: a DB
    leak alone shouldn't let someone reset accounts). Single-use
    (used_at) and short-lived (30 min), unlike refresh tokens which are
    long-lived — a reset token only needs to survive one email-click.
    """

    __tablename__ = "password_reset_tokens"

    id = Column(String(32), primary_key=True, default=_new_id, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    created_at = Column(DateTime, default=_utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="password_reset_tokens")