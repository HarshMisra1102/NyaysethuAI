import json
import re
from typing import Any


def parse_json_response(response: str) -> dict[str, Any]:
    """
    Extract JSON from an LLM response.

    Supports:
    1. Raw JSON
    2. Markdown ```json ... ```
    3. JSON embedded in surrounding text
    """

    if not response or not response.strip():
        raise ValueError(
            "AI returned an empty response."
        )

    text = response.strip()

    # Case 1: Markdown JSON block
    match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if match:
        text = match.group(1).strip()

    # Case 2: Direct JSON
    try:
        result = json.loads(text)

        if not isinstance(result, dict):
            raise ValueError(
                "AI response must be a JSON object."
            )

        return result

    except json.JSONDecodeError:
        pass

    # Case 3: Find JSON object inside text
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No valid JSON object found in AI response."
        )

    try:
        result = json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI returned malformed JSON."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    return result