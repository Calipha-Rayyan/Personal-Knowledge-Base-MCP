from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load embedding model '{self.model_name}'. This is "
                f"usually a network issue downloading from Hugging Face, or a "
                f"corrupted local cache. Try: delete the cached model folder "
                f"under ~/.cache/huggingface/hub and retry. Original error: {e}"
            ) from e
        self.embedding_dim = self._get_embedding_dim()

    def _get_embedding_dim(self) -> int:
        if hasattr(self.model, "get_embedding_dimension"):
            return self.model.get_embedding_dimension()
        return self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        cleaned = [str(t).strip() for t in texts if t is not None and str(t).strip()]
        if not cleaned:
            return []

        try:
            embeddings = self.model.encode(cleaned, convert_to_numpy=True)
            return embeddings.tolist()
        except TypeError:
            results = []
            for text in cleaned:
                embedding = self.model.encode([text], convert_to_numpy=True)
                results.append(embedding[0].tolist())
            return results


_embedder = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder