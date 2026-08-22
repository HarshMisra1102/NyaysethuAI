from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.rights import (
    RightsRequest,
    RightsResponse,
)


router = APIRouter(
    prefix="/rights",
    tags=["Rights"],
)


@router.post(
    "/analyze",
    response_model=RightsResponse,
)
async def analyze_rights(
    data: RightsRequest,
    current_user: User = Depends(get_current_user),
):
    return RightsResponse(
        category=data.category or "GENERAL_CIVIC",
        summary=(
            "AI rights analysis will be available "
            "after AI integration."
        ),
        rights=[],
        action_plan=[],
        required_documents=[],
        sources=[],
        disclaimer=(
            "This information is for general guidance "
            "and is not a substitute for professional "
            "legal advice."
        ),
    )