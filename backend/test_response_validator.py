from app.ai.validators import (
    parse_json_response,
    validate_agent_response,
)


response = """
{
    "issue": "RTI request",
    "category": "Right to Information",
    "summary": "Citizens can request information from public authorities.",
    "possible_rights": [
        "Right to seek information held by a public authority."
    ],
    "action_plan": [
        "Identify the relevant public authority.",
        "Clearly describe the information requested."
    ],
    "required_documents": [
        "Written RTI application"
    ],
    "disclaimer": "This is general information and not legal advice."
}
"""


parsed = parse_json_response(response)

validated = validate_agent_response(
    parsed
)

print("Response validation successful!")
print()
print(validated)