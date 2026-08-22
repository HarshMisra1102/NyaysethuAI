import asyncio

from app.core.database import AsyncSessionLocal
from app.services.document_ingestion_db_service import (
    DocumentDatabaseIngestionService,
)


async def main():

    print("=" * 60)
    print("DATABASE DOCUMENT INGESTION TEST")
    print("=" * 60)

    service = DocumentDatabaseIngestionService()

    async with AsyncSessionLocal() as db:

        document = await service.ingest_file(
            db,
            "test_document.txt",
            title="RTI Test Knowledge Document",
            document_type="knowledge",
            department="RTI",
            language="en",
        )

        print()
        print("Document successfully inserted.")
        print(
            f"Document ID: {document.id}"
        )
        print(
            f"Title: {document.title}"
        )
        print(
            f"Type: {document.document_type}"
        )
        print(
            f"Department: {document.department}"
        )


if __name__ == "__main__":
    asyncio.run(main())