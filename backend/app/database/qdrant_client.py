import os
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter, 
    FieldCondition, MatchValue, FilterSelector
)

from ..ingestion.embedder import get_embedder

COLLECTION_NAME = "document_chunks"

class QdrantManager:
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", 6333))
        self.client = QdrantClient(":memory:")
        self.embedder = get_embedder()
        self.collection_name = os.getenv("QDRANT_COLLECTION", COLLECTION_NAME)
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.embedding_dim,
                    distance=Distance.COSINE
                )
            )

    def store_chunks(self, user_id: str, document_id: str, filename: str, chunks: List[Dict[str, Any]]) -> List[str]:
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed(texts)

        points = []
        for i, chunk in enumerate(chunks):
            point_id = str(uuid.uuid4())
            payload = {
                "user_id": user_id,
                "document_id": document_id,
                "filename": filename,
                "chunk_text": chunk["text"],
                "chunk_index": chunk.get("index", i),
            }
            points.append(PointStruct(id=point_id, vector=embeddings[i], payload=payload))

        self.client.upsert(collection_name=self.collection_name, points=points)
        return [p.id for p in points]

    def search(self, user_id: str, query_text: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        query_vector = self.embedder.embed([query_text])[0]
        
        filter_condition = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
        
        # ✅ FIXED: Using the modern "query_points" method (guaranteed to work!)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=filter_condition,
            score_threshold=score_threshold
        )
        
        # Extract results from the response object
        results = response.points
        
        return [
            {
                "document_id": res.payload["document_id"],
                "filename": res.payload["filename"],
                "chunk_text": res.payload["chunk_text"],
                "score": res.score,
            }
            for res in results
        ]

    def delete_document(self, user_id: str, document_id: str):
        filter_condition = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ]
        )
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(filter=filter_condition)
        )

_qdrant = None

def get_qdrant_manager():
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantManager()
    return 
