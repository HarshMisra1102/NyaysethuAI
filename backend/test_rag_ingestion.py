import asyncio

from app.ai.rag import (
    TextChunker,
    DocumentIngestionService,
    get_embedding_service,
)

from app.core.database import AsyncSessionLocal


async def main():

    text = """
    A citizen may submit an application under the
    Right to Information framework to obtain information
    held by a public authority.

    The application should clearly identify the
    information being requested.

    Citizens should verify the appropriate public
    authority and applicable procedure before submitting
    an application.
    """

    chunker = TextChunker(
        chunk_size=300,
        overlap=50,
    )

    chunks = chunker.chunk_text(text)

    print("Chunks created:", len(chunks))

    embedding_service = (
        get_embedding_service()
    )

    ingestion_service = (
        DocumentIngestionService(
            embedding_service
        )
    )

    async with AsyncSessionLocal() as db:

        count = await ingestion_service.ingest_chunks(
            db=db,
            document_id=1,
            chunks=chunks,
        )

        await db.commit()

        print(
            "Chunks inserted:",
            count,
        )


if __name__ == "__main__":
    asyncio.run(main())