import asyncio

from app.core.database import AsyncSessionLocal
from app.ai.rag.embeddings import get_embedding_service
from app.ai.rag.retriever import VectorRetriever


async def main():

    embedding_service = get_embedding_service()

    retriever = VectorRetriever(
        embedding_service
    )

    queries = [
        "How can I file an RTI request?",
        "My landlord has not returned my security deposit.",
        "I bought a defective product and want a refund.",
        "Am I eligible for a government welfare scheme?",
    ]

    async with AsyncSessionLocal() as db:

        for query in queries:

            print("\n")
            print("=" * 70)
            print("QUERY:")
            print(query)
            print("=" * 70)

            results = await retriever.search(
                db=db,
                query=query,
                top_k=3,
            )

            if not results:
                print("NO RESULTS")
                continue

            for rank, result in enumerate(
                results,
                start=1,
            ):

                print(f"\nRank: {rank}")
                print(
                    f"Chunk ID: {result.chunk_id}"
                )
                print(
                    f"Document ID: "
                    f"{result.document_id}"
                )
                print(
                    f"Similarity: "
                    f"{result.similarity:.4f}"
                )
                print(
                    "Content:"
                )
                print(
                    result.content[:500]
                )


if __name__ == "__main__":
    asyncio.run(main())