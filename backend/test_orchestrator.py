import asyncio

from app.ai.orchestrator import (
    AIOrchestrator,
)


class MockLLM:

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:

        return """
{
    "issue": "Citizen has a tenant-related dispute",
    "category": "Tenant Rights",
    "summary": "The citizen may have rights relating to their tenancy and should review the applicable agreement and official rules.",
    "possible_rights": [
        "The citizen may have protections under applicable tenancy or consumer rules."
    ],
    "action_plan": [
        "Collect the rental agreement and relevant payment records.",
        "Document communications with the landlord.",
        "Verify the applicable local rules.",
        "Consider approaching the appropriate authority if the issue remains unresolved."
    ],
    "required_documents": [
        "Rental agreement",
        "Payment records",
        "Relevant communication records"
    ],
    "disclaimer": "NyayaSetu provides general information and is not a substitute for professional legal advice."
}
"""


async def main():

    orchestrator = AIOrchestrator(
        llm=MockLLM()
    )

    response = await orchestrator.process(
        message=(
            "My landlord has not returned "
            "my ₹20000 security deposit."
        )
    )

    print()
    print("=" * 70)
    print("FINAL CHAT AI RESPONSE")
    print("=" * 70)

    print()

    print("Issue:")
    print(response.issue)

    print()

    print("Category:")
    print(response.category)

    print()

    print("Summary:")
    print(response.summary)

    print()

    print("Possible Rights:")
    print(response.possible_rights)

    print()

    print("Evidence:")
    print(response.evidence)

    print()

    print("Action Plan:")

    for step in response.action_plan:

        print(
            f"{step.step}. "
            f"{step.title}: "
            f"{step.description}"
        )

    print()

    print("Required Documents:")
    print(response.required_documents)

    print()

    print("Sources:")
    print(response.sources)

    print()

    print("Disclaimer:")
    print(response.disclaimer)

    print()

    print("Response Type:")
    print(type(response))

    print()

    print("Validation:")
    print(response.model_dump())


if __name__ == "__main__":
    asyncio.run(main())