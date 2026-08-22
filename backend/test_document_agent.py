import asyncio

from app.ai.agents.document_agent import (
    DocumentAgent,
)


class MockLLM:
    """
    Temporary LLM used for local testing.

    Does not call Gemini.
    """

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:

        return """
        {
            "issue": "Government document explaining an RTI request process",
            "category": "Document Understanding",
            "summary": "The document explains that citizens can seek information held by public authorities and should clearly describe the information requested.",
            "possible_rights": [
                "Right to seek information held by a public authority."
            ],
            "action_plan": [
                "Identify the relevant public authority.",
                "Clearly describe the requested information or records.",
                "Verify the applicable procedure before submitting the request.",
                "Keep a copy of the submitted request and acknowledgement."
            ],
            "required_documents": [
                "Written application describing the requested information"
            ],
            "disclaimer": "NyayaSetu provides general document explanations and is not a substitute for professional legal advice."
        }
        """


async def main():

    agent = DocumentAgent(
        llm=MockLLM()
    )

    evidence = [
        {
            "chunk_id": 1,
            "document_id": 1,
            "page_number": 1,
            "similarity": 0.72,
            "score": 0.69,
            "content": (
                "Right to Information is an important "
                "mechanism through which citizens can seek "
                "information held by public authorities. "
                "An RTI request should clearly describe "
                "the information being requested."
            ),
        },
        {
            "chunk_id": 2,
            "document_id": 1,
            "page_number": 2,
            "similarity": 0.64,
            "score": 0.61,
            "content": (
                "Citizens should identify the relevant "
                "public authority and retain a copy of "
                "their submitted application."
            ),
        },
    ]

    response = await agent.run(
        query=(
            "Explain this government document "
            "in simple language."
        ),
        evidence=evidence,
    )

    print()
    print("=" * 60)
    print("DOCUMENT AGENT TEST")
    print("=" * 60)

    print(response)

    print()
    print("Response type:")
    print(type(response))


if __name__ == "__main__":
    asyncio.run(main())