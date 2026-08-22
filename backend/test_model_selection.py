import asyncio

from app.ai.llm import GeminiClient


async def main():

    client = GeminiClient()

    model = await client._get_model()

    print()
    print("Selected Gemini model:")
    print(model)


if __name__ == "__main__":
    asyncio.run(main())