import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Intent(str, Enum):
    RTI = "RTI"
    RIGHTS = "RIGHTS"
    SCHEME = "SCHEME"
    DOCUMENT = "DOCUMENT"
    GRIEVANCE = "GRIEVANCE"
    GENERAL_CIVIC = "GENERAL_CIVIC"


class IntentResult(BaseModel):
    intent: Intent
    domain: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


CLASSIFICATION_PROMPT = """
Classify the citizen's request into exactly one intent.

Allowed intents:

RTI
RIGHTS
SCHEME
DOCUMENT
GRIEVANCE
GENERAL_CIVIC

Examples:

"I want information about why my scholarship was rejected."
RTI

"My landlord refuses to return my security deposit."
RIGHTS

"Am I eligible for PM-KISAN?"
SCHEME

"Explain this government notice."
DOCUMENT

"Where can I complain about this government service?"
GRIEVANCE

Return ONLY valid JSON:

{
    "intent": "RIGHTS",
    "domain": "TENANT",
    "confidence": 0.95
}
"""


async def classify_intent(
    text: str,
    llm_client: Any,
) -> IntentResult:

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    prompt = f"""
{CLASSIFICATION_PROMPT}

Citizen request:
{text}
"""

    try:
        response = await llm_client.generate(
            prompt=prompt,
            temperature=0.0,
        )

        if isinstance(response, dict):
            data = response
        else:
            cleaned = str(response).strip()

            if cleaned.startswith("```"):
                cleaned = cleaned.replace("```json", "")
                cleaned = cleaned.replace("```", "")
                cleaned = cleaned.strip()

            data = json.loads(cleaned)

        return IntentResult.model_validate(data)

    except Exception:
        return IntentResult(
            intent=Intent.GENERAL_CIVIC,
            domain=None,
            confidence=0.0,
        )