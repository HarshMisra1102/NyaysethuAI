from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    processing_status: str
    title: str
    document_type: str | None
    department: str | None
    language: str | None
    source_url: str | None
    storage_url: str | None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    processing_status: str


class DocumentPage(BaseModel):
    items: list[DocumentResponse]
    page: int
    page_size: int
    total: int
