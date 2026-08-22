import asyncio

from app.ai.agents.rti_agent import RTIAgent


class MockLLM:
    """
    Temporary LLM used for local testing.

    This avoids consuming Gemini API quota.
    """

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:

        return """
        {
            "issue": "Citizen wants to submit an RTI request",
            "category": "Right to Information",
            "summary": "An RTI request can be used to seek information or records held by a public authority.",
            "possible_rights": [
                "Right to seek information and records held by public authorities."
            ],
            "action_plan": [
                "Identify the relevant public authority.",
                "Clearly describe the information or records being requested.",
                "Verify the applicable procedure and fee requirements.",
                "Submit the request to the appropriate authority.",
                "Keep a copy of the submitted request and acknowledgement."
            ],
            "required_documents": [
                "Written RTI application describing the requested information"
            ],
            "disclaimer": "NyayaSetu provides general information and is not a substitute for professional legal advice."
        }
        """


async def main():

    agent = RTIAgent(
        llm=MockLLM()
    )

    evidence = [
        {
            "chunk_id": 1,
            "document_id": 1,
            "page_number": None,
            "similarity": 0.64,
            "score": 0.61,
            "content": (
                "Right to Information is an important "
                "mechanism through which citizens can seek "
                "information held by public authorities."
            ),
        }
    ]

    response = await agent.run(
        query=(
            "How can I request information "
            "from a government department?"
        ),
        evidence=evidence,
    )

    print()
    print("=" * 60)
    print("RTI AGENT TEST")
    print("=" * 60)

    print(response)

    print()
    print("Response type:")
    print(type(response))


if __name__ == "__main__":
    asyncio.run(main())