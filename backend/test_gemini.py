import asyncio

from app.ai.llm import GeminiClient


async def main():

    client = GeminiClient()

    response = await client.generate(
        """
        Explain RTI in India in one simple sentence.
        Do not provide legal advice.
        """
    )

    print("\nGemini response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())