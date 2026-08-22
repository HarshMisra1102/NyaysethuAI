import asyncio

from sqlalchemy import text

from app.core.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:

        result = await db.execute(
            text("SELECT COUNT(*) FROM document_chunks")
        )

        count = result.scalar_one()

        print(f"Document chunks: {count}")


if __name__ == "__main__":
    asyncio.run(main())