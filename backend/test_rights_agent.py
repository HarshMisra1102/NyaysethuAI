import asyncio

from app.ai.agents.rights_agent import RightsAgent
from app.ai.rag import (
    Reranker,
    VectorRetriever,
    get_embedding_service,
)
from app.core.database import AsyncSessionLocal


async def main():

    query = (
        "How can a citizen request information "
        "from a government authority?"
    )

    embedding_service = (
        get_embedding_service()
    )

    retriever = VectorRetriever(
        embedding_service
    )

    reranker = Reranker()

    async with AsyncSessionLocal() as db:

        retrieved = await retriever.search(
            db=db,
            query=query,
            top_k=8,
        )

        ranked = reranker.rerank(
            query=query,
            chunks=retrieved,
            top_k=5,
        )

    evidence = [
        {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "score": chunk.final_score,
            "content": chunk.content,
        }
        for chunk in ranked
    ]

    agent = RightsAgent()

    response = await agent.run(
        query=query,
        evidence=evidence,
    )

    print("\n===== RIGHTS AGENT =====\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())