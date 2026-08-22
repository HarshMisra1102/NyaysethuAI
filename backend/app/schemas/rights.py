from pydantic import BaseModel, Field


class RightsRequest(BaseModel):
    problem: str = Field(
        min_length=5,
        max_length=10000,
    )

    category: str | None = None

    state: str | None = None
    district: str | None = None


class RightItem(BaseModel):
    title: str
    explanation: str
    legal_basis: str | None = None


class RightsResponse(BaseModel):
    category: str
    summary: str
    rights: list[RightItem] = []
    action_plan: list[str] = []
    required_documents: list[str] = []
    sources: list[str] = []
    disclaimer: str