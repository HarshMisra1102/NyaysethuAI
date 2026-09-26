from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_ingestion_service import (
    DocumentIngestionService,
)


class DocumentDatabaseIngestionService:
    """
    Converts a physical document into database records.

    Pipeline:

        File
          ↓
        Text extraction
          ↓
        Chunking
          ↓
        Embeddings
          ↓
        Document
          ↓
        DocumentChunk
          ↓
        PostgreSQL / pgvector
    """

    def __init__(
        self,
        ingestion_service: DocumentIngestionService | None = None,
    ):
        self.ingestion_service = (
            ingestion_service
            or DocumentIngestionService()
        )

    async def ingest_file(
        self,
        db: AsyncSession,
        file_path: str | Path,
        *,
        title: str | None = None,
        document_type: str = "knowledge",
        department: str | None = None,
        language: str | None = "en",
        source_url: str | None = None,
        storage_url: str | None = None,
        user_id: int | None = None,
    ) -> Document:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        # --------------------------------------------------
        # Extract + chunk + embed
        # --------------------------------------------------

        chunks = self.ingestion_service.process_file(
            path
        )

        if not chunks:
            raise ValueError(
                "No readable content was found."
            )

        # --------------------------------------------------
        # Create document
        # --------------------------------------------------

        document = Document(
            user_id=user_id,
            title=title or path.stem,
            document_type=document_type,
            department=department,
            language=language,
            source_url=source_url,
            storage_url=storage_url,
        )

        db.add(document)

        # Flush so document.id becomes available.
        await db.flush()

        # --------------------------------------------------
        # Create chunks
        # --------------------------------------------------

        for chunk in chunks:

            document_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk.content,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                embedding=chunk.embedding,
            )

            db.add(document_chunk)

        # --------------------------------------------------
        # Commit everything
        # --------------------------------------------------

        await db.commit()

        # Refresh document from database.
        await db.refresh(document)

        return document
