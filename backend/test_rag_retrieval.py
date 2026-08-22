import asyncio

from app.ai.rag import (
    Reranker,
    VectorRetriever,
    get_embedding_service,
)

from app.core.database import AsyncSessionLocal


async def main():

    embedding_service = get_embedding_service()

    retriever = VectorRetriever(
        embedding_service
    )

    reranker = Reranker()

    query = (
        "What information can a citizen "
        "request from a government authority?"
    )

    async with AsyncSessionLocal() as db:

        retrieved = await retriever.search(
            db=db,
            query=query,
            top_k=8,
        )

        print(
            f"\nRetrieved {len(retrieved)} chunks"
        )

        ranked = reranker.rerank(
            query=query,
            chunks=retrieved,
            top_k=5,
        )

        print(
            f"\nReranked {len(ranked)} chunks\n"
        )

        for index, chunk in enumerate(
            ranked,
            start=1,
        ):

            print("=" * 70)

            print(
                f"Rank: {index}"
            )

            print(
                f"Chunk ID: {chunk.chunk_id}"
            )

            print(
                f"Document ID: {chunk.document_id}"
            )

            print(
                f"Similarity: "
                f"{chunk.similarity:.4f}"
            )

            print(
                f"Final Score: "
                f"{chunk.final_score:.4f}"
            )

            print(
                f"Content:\n{chunk.content}"
            )


if __name__ == "__main__":
    asyncio.run(main())