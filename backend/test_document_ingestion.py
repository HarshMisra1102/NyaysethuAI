from app.services.document_ingestion_service import (
    DocumentIngestionService,
)


def main():
    print("=" * 60)
    print("DOCUMENT INGESTION TEST")
    print("=" * 60)

    service = DocumentIngestionService(
        chunk_size=300,
        chunk_overlap=50,
    )

    file_path = "test_document.txt"

    print("\n1. Processing document...")

    chunks = service.process_file(
        file_path
    )

    print(
        f"\nCreated chunks: {len(chunks)}"
    )

    for chunk in chunks:

        print("\n" + "-" * 60)

        print(
            f"Chunk index: {chunk.chunk_index}"
        )

        print(
            f"Page: {chunk.page_number}"
        )

        print(
            f"Characters: {len(chunk.content)}"
        )

        print(
            f"Embedding dimension: "
            f"{len(chunk.embedding)}"
        )

        print("\nContent:")
        print(chunk.content[:500])


if __name__ == "__main__":
    main()