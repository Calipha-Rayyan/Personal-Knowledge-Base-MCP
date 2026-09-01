from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self._get_embedding_dim()

    def _get_embedding_dim(self) -> int:
        # Newer sentence-transformers versions renamed this method; older
        # ones only have the original name. Try both so this works
        # regardless of which version is installed.
        if hasattr(self.model, "get_embedding_dimension"):
            return self.model.get_embedding_dimension()
        return self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


_embedder = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder