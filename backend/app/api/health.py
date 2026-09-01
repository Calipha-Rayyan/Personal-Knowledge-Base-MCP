from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal
from app.database.qdrant_client import get_qdrant_manager

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    """Basic liveness check — the process is up and responding."""
    return {"status": "ok"}


@router.get("/health/db")
def health_db():
    """Checks the application database is actually reachable."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "component": "database"}
    except Exception as e:
        return {"status": "error", "component": "database", "detail": str(e)}


@router.get("/health/qdrant")
def health_qdrant():
    """Checks Qdrant is reachable and the expected collection exists."""
    try:
        manager = get_qdrant_manager()
        collections = [c.name for c in manager.client.get_collections().collections]
        return {
            "status": "ok",
            "component": "qdrant",
            "collection_exists": manager.collection_name in collections,
        }
    except Exception as e:
        return {"status": "error", "component": "qdrant", "detail": str(e)}