"""Local BGE embedding model using sentence-transformers."""
from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

logger = logging.getLogger(__name__)


class LocalBGEEmbedder:
    """Sentence transformer embedder using BAAI/bge-large-en-v1.5."""

    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s on %s", self.model_name, self.device)
            self._model = SentenceTransformer(self.model_name, device=self.device)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts and return vectors."""
        model = self._load_model()
        # BGE models perform better with query instruction prefix for retrieval
        prefixed = [f"Represent this document for retrieval: {t}" for t in texts]
        embeddings = model.encode(prefixed, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Embed a single search query."""
        model = self._load_model()
        prefixed = f"Represent this query for retrieving relevant documents: {query}"
        embedding = model.encode([prefixed], normalize_embeddings=True)
        return embedding[0].tolist()

    @property
    def dimension(self) -> int:
        return 1024
