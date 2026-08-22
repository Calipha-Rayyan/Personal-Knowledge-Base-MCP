from .loader import extract_text
from .chunker import chunk_text
from ..database.qdrant_client import get_qdrant_manager

def process_document(file_path: str, user_id: str, document_id: str, filename: str):
    """
    The main magic button for Teammate 3.
    Give it a file path, user_id, and doc_id, and it does everything.
    """
    # 1. Read the file
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise ValueError("The file is empty or could not be read.")

    # 2. Chop it into chunks
    chunks = chunk_text(raw_text)
    if not chunks:
        raise ValueError("Could not split the text into chunks.")

    # 3. Store them on the shelf
    qdrant = get_qdrant_manager()
    chunk_ids = qdrant.store_chunks(
        user_id=user_id,
        document_id=document_id,
        filename=filename,
        chunks=chunks
    )
    return chunk_ids

def search_vectors(user_id: str, query: str, top_k: int = 5, score_threshold: float = 0.0):
    """The magic button for Teammate 1 (MCP) to search."""
    qdrant = get_qdrant_manager()
    return qdrant.search(user_id, query, top_k, score_threshold)

def delete_document(user_id: str, document_id: str):
    """Teammate 3 uses this to delete a file."""
    qdrant = get_qdrant_manager()
    qdrant.delete_document(user_id, document_id)
    