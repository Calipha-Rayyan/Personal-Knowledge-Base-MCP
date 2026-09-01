from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.services.search_service import get_search_service

router = APIRouter(tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = settings.search_top_k_default
    file_type: str | None = None
    document_id: str | None = None


@router.post("/search")
def search(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    query = payload.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    service = get_search_service()
    results = service.search_notes(
        user_id=str(current_user.id),
        query=query,
        top_k=payload.top_k,
        file_type=payload.file_type,
        document_id=payload.document_id,
    )

    if not results:
        return {"query": query, "results": [], "message": "No confident match found."}

    return {"query": query, "results": results}