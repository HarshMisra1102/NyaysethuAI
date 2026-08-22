from app.ai.llm import GeminiClient
from app.ai.prompts.rti import RTI_SYSTEM_PROMPT
from app.ai.validators import (
    parse_json_response,
    validate_agent_response,
)


class RTIAgent:
    """
    RTI assistance agent.

    Uses RAG evidence to help citizens understand
    and prepare RTI-related actions.
    """

    def __init__(
        self,
        llm: GeminiClient | None = None,
    ):
        self.llm = llm or GeminiClient()

    async def run(
        self,
        query: str,
        evidence: list[dict],
    ) -> dict:

        evidence_text = self._format_evidence(
            evidence
        )

        prompt = f"""
{RTI_SYSTEM_PROMPT}

USER QUESTION:
{query}

RETRIEVED EVIDENCE:
{evidence_text}

Based on the user's question and the retrieved
evidence, produce a practical RTI-oriented response.

Remember:

- Do not invent information.
- Use only supported facts.
- Mention uncertainty where evidence is insufficient.
- Return valid JSON only.
"""

        raw_response = await self.llm.generate(
            prompt,
            temperature=0.1,
        )

        parsed_response = parse_json_response(
            raw_response
        )

        validated_response = (
            validate_agent_response(
                parsed_response
            )
        )

        return validated_response

    @staticmethod
    def _format_evidence(
        evidence: list[dict],
    ) -> str:

        if not evidence:
            return (
                "NO RELIABLE EVIDENCE WAS RETRIEVED."
            )

        sections = []

        for index, item in enumerate(
            evidence,
            start=1,
        ):
            sections.append(
                f"""
[EVIDENCE {index}]
Chunk ID: {item.get("chunk_id")}
Document ID: {item.get("document_id")}
Page: {item.get("page_number")}
Similarity: {item.get("similarity")}
Score: {item.get("score")}

{item.get("content", "")}
"""
            )

        return "\n".join(sections)