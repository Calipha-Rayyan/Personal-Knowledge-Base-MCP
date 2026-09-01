from typing import Optional

from app.ingestion.loader import extract_text
from app.ingestion.chunker import chunk_text
from app.database.qdrant_client import get_qdrant_manager


def process_document(file_path: str, user_id: str, document_id: str, filename: str):
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise ValueError("The file is empty or could not be read.")

    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("Could not split the text into chunks.")

    file_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else None

    qdrant = get_qdrant_manager()
    chunk_ids = qdrant.store_chunks(
        user_id=user_id,
        document_id=document_id,
        filename=filename,
        chunks=chunks,
        file_type=file_type,
    )
    return chunk_ids


def search_vectors(
    user_id: str,
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.0,
    file_type: Optional[str] = None,
    document_id: Optional[str] = None,
):
    qdrant = get_qdrant_manager()
    return qdrant.search(
        user_id, query, top_k, score_threshold,
        file_type=file_type, document_id=document_id,
    )


def get_document_chunks(user_id: str, document_id: str):
    qdrant = get_qdrant_manager()
    return qdrant.get_document_chunks(user_id, document_id)


def delete_document_vectors(user_id: str, document_id: str):
    qdrant = get_qdrant_manager()
    qdrant.delete_document(user_id, document_id)