from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.ingestion.processor import search_vectors, get_document_chunks
from app.models.document import Document


class SearchService:
    """
    Single, real implementation of search/document/source access.

    This is the ONE place that both the FastAPI `/search` route and the
    MCP tools (search_notes / get_document / list_sources) call into, so
    there is no second, duplicate Qdrant/search implementation.

    User isolation is enforced here (and again at the Qdrant filter level
    in qdrant_client.py) by always scoping lookups to `user_id`.
    """

    def _db(self) -> Session:
        return SessionLocal()

    def search_notes(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return []

        top_k = max(1, min(top_k, settings.search_top_k_max))

        raw_results = search_vectors(
            user_id=user_id,
            query=query,
            top_k=top_k,
            score_threshold=settings.search_score_threshold,
        )
        return raw_results

    def get_document(
        self,
        user_id: str,
        doc_id: str,
    ) -> dict[str, Any]:
        db = self._db()
        try:
            doc = (
                db.query(Document)
                .filter(Document.id == doc_id, Document.user_id == int(user_id))
                .first()
            )
            if not doc:
                return {
                    "document_id": doc_id,
                    "filename": "Not found",
                    "content": "",
                }

            chunks = get_document_chunks(user_id=user_id, document_id=doc_id)
            content = "\n\n".join(c["chunk_text"] for c in chunks)

            return {
                "document_id": doc.id,
                "filename": doc.filename,
                "content": content,
            }
        finally:
            db.close()

    def list_sources(
        self,
        user_id: str,
    ) -> list[dict[str, Any]]:
        db = self._db()
        try:
            docs = (
                db.query(Document)
                .filter(Document.user_id == int(user_id))
                .order_by(Document.uploaded_at.desc())
                .all()
            )
            return [
                {"document_id": d.id, "filename": d.filename}
                for d in docs
            ]
        finally:
            db.close()


_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
