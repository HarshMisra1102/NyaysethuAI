import json
from typing import Any

from pydantic import BaseModel, Field


class ExtractedEntities(BaseModel):
    state: str | None = None
    district: str | None = None
    department: str | None = None
    scheme: str | None = None
    issue: str | None = None
    service: str | None = None
    organization: str | None = None
    document_type: str | None = None

    dates: list[str] = Field(default_factory=list)
    additional_entities: dict[str, str] = Field(default_factory=dict)


ENTITY_PROMPT = """
Extract relevant civic/government entities from the citizen's message.

Extract when present:

- state
- district
- department
- scheme
- issue
- service
- organization
- document_type
- dates

Do NOT guess missing information.

Do NOT infer a specific department unless explicitly stated.

Return ONLY JSON.

Example:

{
    "state": "Uttar Pradesh",
    "district": null,
    "department": null,
    "scheme": "PM-KISAN",
    "issue": "Application rejected",
    "service": null,
    "organization": null,
    "document_type": null,
    "dates": [],
    "additional_entities": {}
}
"""


async def extract_entities(
    text: str,
    llm_client: Any,
) -> ExtractedEntities:

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    prompt = f"""
{ENTITY_PROMPT}

Citizen message:
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

        return ExtractedEntities.model_validate(data)

    except Exception:
        return ExtractedEntities()