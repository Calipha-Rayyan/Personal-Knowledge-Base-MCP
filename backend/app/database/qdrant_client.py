import uuid
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, FilterSelector
)

from app.core.config import settings
from app.ingestion.embedder import get_embedder


class QdrantManager:
    def __init__(self):
        self.embedder = get_embedder()
        self.collection_name = settings.qdrant_collection

        if settings.qdrant_in_memory:
            # Good for local dev / demos without a running Qdrant server.
            # NOTE: data does not persist across process restarts in this mode.
            self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )

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

    def store_chunks(
        self,
        user_id: str,
        document_id: str,
        filename: str,
        chunks: List[Dict[str, Any]],
    ) -> List[str]:
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed(texts)

        points = []
        point_ids = []
        for i, chunk in enumerate(chunks):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)
            payload = {
                "user_id": str(user_id),
                "document_id": document_id,
                "filename": filename,
                "chunk_text": chunk["text"],
                "chunk_index": chunk.get("index", i),
            }
            points.append(
                PointStruct(id=point_id, vector=embeddings[i], payload=payload)
            )

        self.client.upsert(collection_name=self.collection_name, points=points)
        return point_ids

    def search(
        self,
        user_id: str,
        query_text: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        query_vector = self.embedder.embed([query_text])[0]

        # Multi-user isolation: every query is filtered to the requesting
        # user's own points, at the Qdrant layer (not just in the API/UI).
        filter_condition = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))]
        )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=filter_condition,
            score_threshold=score_threshold,
        )

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

    def get_document_chunks(
        self, user_id: str, document_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch all stored chunks for one document, ordered by chunk_index."""
        filter_condition = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
                FieldCondition(key="document_id", match=MatchValue(value=document_id)),
            ]
        )
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter_condition,
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )
        chunks = [
            {
                "chunk_index": p.payload.get("chunk_index", 0),
                "chunk_text": p.payload["chunk_text"],
            }
            for p in points
        ]
        chunks.sort(key=lambda c: c["chunk_index"])
        return chunks

    def delete_document(self, user_id: str, document_id: str):
        filter_condition = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=str(user_id))),
                FieldCondition(key="document_id", match=MatchValue(value=document_id)),
            ]
        )
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(filter=filter_condition),
        )


_qdrant: QdrantManager | None = None


def get_qdrant_manager() -> QdrantManager:
    global _qdrant
    if _qdrant is None:
        _qdrant = QdrantManager()
    return _qdrant
