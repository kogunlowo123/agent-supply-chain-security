"""RAG Core service settings."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/supply_chain_security"
    opensearch_url: str = "https://localhost:9200"
    opensearch_username: str = "admin"
    opensearch_password: str = "admin"

    embedding_model: str = "BAAI/bge-large-en-v1.5"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    embedding_dimension: int = 1024

    chunk_size: int = 512
    chunk_overlap: int = 64

    retrieval_top_k: int = 5
    reranker_top_n: int = 3


@lru_cache
def get_rag_settings() -> RAGSettings:
    return RAGSettings()
