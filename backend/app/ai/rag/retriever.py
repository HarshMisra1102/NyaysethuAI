from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.embeddings import EmbeddingService
from app.models.document_chunk import DocumentChunk


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    content: str
    page_number: int | None
    similarity: float


class VectorRetriever:
    """
    Retrieves relevant document chunks from Neon PostgreSQL
    using pgvector cosine similarity.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ):
        self.embedding_service = embedding_service

    async def search(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = 8,
    ) -> list[RetrievedChunk]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        # Generate query embedding.
        query_embedding = (
            self.embedding_service.embed_text(query)
        )

        # pgvector cosine distance.
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # Convert distance to similarity.
        similarity = 1 - distance

        statement = (
            select(
                DocumentChunk,
                similarity.label("similarity"),
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(top_k)
        )

        result = await db.execute(statement)

        rows = result.all()

        retrieved: list[RetrievedChunk] = []

        for chunk, score in rows:

            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    similarity=float(score),
                )
            )

        return retrieved