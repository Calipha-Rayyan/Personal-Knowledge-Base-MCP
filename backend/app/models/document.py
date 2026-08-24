import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


class Document(Base):
    """
    Application-database record of an uploaded document.

    This is metadata only (ownership, filename, timestamps). The actual
    chunk text + embeddings live in Qdrant, keyed by this document's id
    (document_id) and the owning user's id (user_id), so that vector
    search can be filtered per-user.
    """

    __tablename__ = "documents"

    id = Column(String(32), primary_key=True, default=_new_id, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    chunk_count = Column(Integer, default=0)

    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="documents")
