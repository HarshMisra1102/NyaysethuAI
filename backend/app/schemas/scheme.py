from pydantic import BaseModel, Field


class SchemeEligibilityRequest(BaseModel):
    scheme_name: str | None = None

    age: int | None = Field(
        default=None,
        ge=0,
        le=150,
    )

    state: str | None = None
    district: str | None = None

    occupation: str | None = None
    annual_income: float | None = Field(
        default=None,
        ge=0,
    )

    category: str | None = None


class SchemeResponse(BaseModel):
    scheme_name: str
    eligible: bool | None
    confidence: float | None = None
    explanation: str
    eligibility_conditions: list[str] = []
    missing_information: list[str] = []
    application_url: str | None = None
    sources: list[str] = []
    disclaimer: str