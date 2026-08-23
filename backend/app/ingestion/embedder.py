import os
from sentence_transformers import SentenceTransformer
from typing import List

DEFAULT_MODEL = "all-MiniLM-L6-v2"

class Embedder:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL)
        self.model = SentenceTransformer(self.model_name)
        # FIXED: Using the new method name to remove the warning
        self.embedding_dim = self.model.get_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder