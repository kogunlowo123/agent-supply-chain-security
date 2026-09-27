"""pgvector vector store implementation."""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


class PGVectorStore:
    """Store and retrieve document chunks using PostgreSQL pgvector."""

    def __init__(self, connection_string: str, table_name: str = "document_chunks"):
        self.connection_string = connection_string
        self.table_name = table_name

    def _get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        conn.autocommit = False
        return conn

    def upsert(self, chunks: list[dict[str, Any]]) -> int:
        """Insert or update document chunks with embeddings."""
        if not chunks:
            return 0

        conn = self._get_connection()
        inserted = 0
        try:
            with conn.cursor() as cur:
                for chunk in chunks:
                    cur.execute(
                        f"""
                        INSERT INTO {self.table_name}
                            (id, doc_id, chunk_index, content, embedding, metadata, source_url)
                        VALUES (%s, %s, %s, %s, %s::vector, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                        """,
                        (
                            chunk.get("id", str(uuid.uuid4())),
                            chunk["doc_id"],
                            chunk["chunk_index"],
                            chunk["content"],
                            chunk["embedding"],
                            json.dumps(chunk.get("metadata", {})),
                            chunk.get("source_url"),
                        ),
                    )
                    inserted += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

        return inserted

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Find most similar chunks by cosine similarity."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
                cur.execute(
                    f"""
                    SELECT id, doc_id, chunk_index, content, metadata, source_url,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM {self.table_name}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (embedding_str, embedding_str, top_k),
                )
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()
