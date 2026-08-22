import asyncio

from app.ai.agents.scheme_agent import SchemeAgent


class MockLLM:
    """
    Temporary LLM for local testing.

    Does not call Gemini.
    """

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:

        return """
        {
            "issue": "Citizen wants to know whether a government scheme may apply to them",
            "category": "Government Scheme",
            "summary": "Government schemes may provide benefits to eligible citizens, but eligibility must be checked against the official criteria.",
            "possible_rights": [
                "Right to receive information about applicable government schemes.",
                "Right to apply for a scheme when the official eligibility criteria are satisfied."
            ],
            "action_plan": [
                "Identify the government scheme relevant to the citizen's situation.",
                "Compare the citizen's details with the official eligibility criteria.",
                "Collect the documents required by the scheme.",
                "Verify the current eligibility requirements with the official government department or portal.",
                "Submit an application through the official process if eligible."
            ],
            "required_documents": [
                "Identity document",
                "Address or residence proof",
                "Any scheme-specific supporting documents"
            ],
            "disclaimer": "NyayaSetu provides general information and cannot confirm official scheme eligibility. Final eligibility should be verified through the relevant government authority or official portal."
        }
        """


async def main():

    agent = SchemeAgent(
        llm=MockLLM()
    )

    evidence = [
        {
            "chunk_id": 10,
            "document_id": 5,
            "page_number": 1,
            "similarity": 0.71,
            "score": 0.68,
            "content": (
                "Government schemes may provide benefits "
                "to eligible citizens. Applicants should "
                "verify the applicable eligibility criteria "
                "and required documents through the "
                "relevant government authority."
            ),
        }
    ]

    response = await agent.run(
        query=(
            "I want to know whether I may be eligible "
            "for a government welfare scheme."
        ),
        evidence=evidence,
    )

    print()
    print("=" * 60)
    print("SCHEME AGENT TEST")
    print("=" * 60)

    print(response)

    print()
    print("Response type:")
    print(type(response))


if __name__ == "__main__":
    asyncio.run(main())