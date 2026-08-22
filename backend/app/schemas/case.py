from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    category: str = Field(
        min_length=2,
        max_length=50,
    )

    description: str = Field(
        min_length=5,
    )


class CaseUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class CaseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    title: str
    category: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime