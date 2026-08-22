from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.document import (
    DocumentUploadResponse,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=501,
        detail=(
            "Document upload and processing will be "
            "implemented with the document-processing "
            "pipeline."
        ),
    )