import uuid
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, FilterSelector, PayloadSchemaType
)

from app.core.config import settings
from app.ingestion.embedder import get_embedder


class QdrantManager:
    def __init__(self):
        self.embedder = get_embedder()
        self.collection_name = settings.qdrant_collection

        if settings.qdrant_in_memory:
            self.client = QdrantClient(":memory:")
        elif settings.qdrant_api_key:
            scheme = "https" if settings.qdrant_use_https else "http"
            self.client = QdrantClient(
                url=f"{scheme}://{settings.qdrant_host}:{settings.qdrant_port}",
                api_key=settings.qdrant_api_key,
            )
        else:
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )

        self._ensure_collection()
        self._ensure_indexes()

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

    def _ensure_indexes(self):
        """
        Newer/managed Qdrant instances (including Qdrant Cloud) require
        an explicit payload index on any field used in a filter — unlike
        older local Qdrant, which allowed filtering unindexed fields.
        Creating an index that already exists is a harmless no-op, so
        this is safe to call on every startup rather than needing a
        one-time migration step.
        """
        indexed_fields = {
            "user_id": PayloadSchemaType.KEYWORD,
            "document_id": PayloadSchemaType.KEYWORD,
            "file_type": PayloadSchemaType.KEYWORD,
        }
        for field_name, schema_type in indexed_fields.items():
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=schema_type,
                )
            except Exception:
                # Index likely already exists (older qdrant-client
                # versions raise instead of silently succeeding on a
                # duplicate index request). Safe to ignore.
                pass

    def store_chunks(
        self,
        user_id: str,
        document_id: str,
        filename: str,
        chunks: List[Dict[str, Any]],
        file_type: Optional[str] = None,
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
                "file_type": file_type,
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
        file_type: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_vector = self.embedder.embed([query_text])[0]

        must_conditions = [
            FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))
        ]
        if file_type:
            must_conditions.append(
                FieldCondition(key="file_type", match=MatchValue(value=file_type.lstrip(".")))
            )
        if document_id:
            must_conditions.append(
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            )

        filter_condition = Filter(must=must_conditions)

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

    def get_document_chunks(self, user_id: str, document_id: str) -> List[Dict[str, Any]]:
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