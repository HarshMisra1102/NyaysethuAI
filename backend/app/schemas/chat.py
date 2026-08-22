from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    case_id: int | None = None

    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class Citation(BaseModel):
    title: str
    url: str | None = None
    source_type: str | None = None
    document_id: int | None = None
    page_number: int | None = None


class Evidence(BaseModel):
    content: str
    document_id: int | None = None
    chunk_id: int | None = None
    page_number: int | None = None
    score: float | None = None
    source: Citation | None = None


class ActionStep(BaseModel):
    step: int
    title: str
    description: str


class ChatAIResponse(BaseModel):
    issue: str | None = None
    category: str | None = None
    summary: str
    possible_rights: list[str] = []
    evidence: list[Evidence] = []
    action_plan: list[ActionStep] = []
    required_documents: list[str] = []
    sources: list[Citation] = []
    disclaimer: str


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    response: ChatAIResponse
    created_at: datetime