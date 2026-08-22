from pydantic import BaseModel, Field


class RTIRequest(BaseModel):
    question: str = Field(
        min_length=5,
        max_length=10000,
    )

    state: str | None = None
    district: str | None = None

    applicant_name: str | None = None
    applicant_address: str | None = None


class RTIDraft(BaseModel):
    department: str
    public_information_officer: str | None = None
    subject: str
    application_text: str
    required_documents: list[str] = []
    submission_method: str | None = None
    submission_url: str | None = None
    sources: list[str] = []
    disclaimer: str