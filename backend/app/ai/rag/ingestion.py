from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.chunker import TextChunk
from app.ai.rag.embeddings import EmbeddingService
from app.models.document_chunk import DocumentChunk


class DocumentIngestionService:
    """
    Converts processed text chunks into embeddings and stores them
    in the existing document_chunks table.

    Database transaction ownership remains with the caller.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ):
        self.embedding_service = embedding_service

    async def ingest_chunks(
        self,
        db: AsyncSession,
        document_id: int,
        chunks: list[TextChunk],
    ) -> int:

        if not chunks:
            return 0

        texts = [
            chunk.content
            for chunk in chunks
            if chunk.content and chunk.content.strip()
        ]

        if not texts:
            return 0

        embeddings = (
            self.embedding_service.embed_documents(
                texts
            )
        )

        records = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            record = DocumentChunk(
                document_id=document_id,
                content=chunk.content,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            )

            records.append(record)

        db.add_all(records)

        await db.flush()

        return len(records)