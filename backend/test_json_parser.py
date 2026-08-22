from app.ai.validators.json_parser import parse_json_response

response = '{"issue": "RTI request", "category": "Right to Information", "summary": "Citizens can request information.", "possible_rights": ["Right to seek information held by a public authority."], "action_plan": ["Identify the relevant public authority."], "required_documents": ["Written RTI application"], "disclaimer": "This is general information and not legal advice."}'

result = parse_json_response(response)

print("Parser successful:")
print(result)

print()
print("Type:", type(result))