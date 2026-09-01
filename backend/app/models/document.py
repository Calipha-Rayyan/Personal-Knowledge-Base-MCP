import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Allowed values for Document.status. Kept as plain strings (not a DB-level
# enum) to stay portable across SQLite/Postgres and avoid migration pain
# when new states are added later.
class DocumentStatus:
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Document(Base):
    """
    Application-database record of an uploaded document.

    This is metadata only (ownership, filename, timestamps, processing
    status). The actual chunk text + embeddings live in Qdrant, keyed by
    this document's id (document_id) and the owning user's id (user_id).
    """

    __tablename__ = "documents"

    id = Column(String(32), primary_key=True, default=_new_id, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    chunk_count = Column(Integer, default=0)

    status = Column(String(20), nullable=False, default=DocumentStatus.UPLOADING)
    error_message = Column(Text, nullable=True)

    # uploaded_at is kept (not renamed) so existing rows and any code
    # still reading it continue to work unmodified.
    uploaded_at = Column(DateTime, default=_utcnow)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="documents")