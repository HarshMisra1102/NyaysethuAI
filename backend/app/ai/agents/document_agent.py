from app.ai.llm import GeminiClient
from app.ai.prompts.document import (
    DOCUMENT_SYSTEM_PROMPT,
)
from app.ai.validators import (
    parse_json_response,
    validate_agent_response,
)


class DocumentAgent:
    """
    Document understanding agent.

    Uses retrieved document evidence to explain
    civic and legal documents in simple language.
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
{DOCUMENT_SYSTEM_PROMPT}

USER QUESTION:
{query}

DOCUMENT EVIDENCE:
{evidence_text}

Analyze the document evidence and explain it
in simple language.

Important:

- Stay grounded in the supplied evidence.
- Do not invent missing information.
- If the evidence does not answer something,
  clearly state that it is not available.
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
                "NO RELIABLE DOCUMENT EVIDENCE "
                "WAS RETRIEVED."
            )

        sections = []

        for index, item in enumerate(
            evidence,
            start=1,
        ):
            sections.append(
                f"""
[DOCUMENT EVIDENCE {index}]
Chunk ID: {item.get("chunk_id")}
Document ID: {item.get("document_id")}
Page: {item.get("page_number")}
Similarity: {item.get("similarity")}
Score: {item.get("score")}

{item.get("content", "")}
"""
            )

        return "\n".join(sections)