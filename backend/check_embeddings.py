import asyncio

from sqlalchemy import text

from app.core.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:

        result = await db.execute(
            text("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(embedding) AS with_embedding
                FROM document_chunks
            """)
        )

        row = result.one()

        print(f"Total chunks: {row.total}")
        print(f"Chunks with embeddings: {row.with_embedding}")


if __name__ == "__main__":
    asyncio.run(main())