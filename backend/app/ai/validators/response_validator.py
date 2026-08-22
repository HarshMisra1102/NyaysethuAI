from typing import Any


REQUIRED_FIELDS = {
    "issue",
    "category",
    "summary",
    "possible_rights",
    "action_plan",
    "required_documents",
    "disclaimer",
}


def validate_agent_response(
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the basic structure returned by an AI agent.

    This validator intentionally does not validate
    evidence or sources because those must come from
    the RAG/database layer rather than the LLM.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    missing = REQUIRED_FIELDS - data.keys()

    if missing:
        raise ValueError(
            "AI response is missing required fields: "
            + ", ".join(sorted(missing))
        )

    if not isinstance(
        data["possible_rights"],
        list,
    ):
        raise ValueError(
            "possible_rights must be a list."
        )

    if not isinstance(
        data["action_plan"],
        list,
    ):
        raise ValueError(
            "action_plan must be a list."
        )

    if not isinstance(
        data["required_documents"],
        list,
    ):
        raise ValueError(
            "required_documents must be a list."
        )

    for field in [
        "summary",
        "disclaimer",
    ]:
        if not isinstance(
            data[field],
            str,
        ):
            raise ValueError(
                f"{field} must be a string."
            )

    return data