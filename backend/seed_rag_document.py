import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.chunker import TextChunker
from app.ai.rag.embeddings import get_embedding_service
from app.ai.rag.ingestion import DocumentIngestionService
from app.core.database import AsyncSessionLocal
from app.models.document import Document


DOCUMENT_TEXT = """
Right to Information is an important mechanism through which citizens
can seek information held by public authorities.

An RTI request should clearly describe the information being requested.
The citizen should identify the relevant public authority as accurately
as possible.

A request should focus on information or records held by the authority.
Citizens should verify the applicable procedure, authority and fee
requirements before submitting an application.

Government information may include records, documents, orders, reports,
circulars and other material held by a public authority.

Citizens should retain a copy of their submitted application and any
acknowledgement received from the authority.
"""


async def create_document(
    db: AsyncSession,
) -> Document:

    document = Document(
        title="RTI Citizen Information Guide - Development Seed",
        document_type="RTI_GUIDE",
        department="Public Authority",
        language="English",
        source_url=None,
        storage_url=None,
    )

    db.add(document)

    await db.flush()

    return document


async def main():

    async with AsyncSessionLocal() as db:

        document = await create_document(db)

        print(
            f"Created document with ID: {document.id}"
        )

        chunker = TextChunker(
            chunk_size=500,
            overlap=75,
        )

        chunks = chunker.chunk_text(
            DOCUMENT_TEXT
        )

        print(
            f"Created {len(chunks)} chunks"
        )

        embedding_service = (
            get_embedding_service()
        )

        ingestion_service = (
            DocumentIngestionService(
                embedding_service
            )
        )

        count = await ingestion_service.ingest_chunks(
            db=db,
            document_id=document.id,
            chunks=chunks,
        )

        await db.commit()

        print(
            f"Inserted {count} embedded chunks"
        )


if __name__ == "__main__":
    asyncio.run(main())