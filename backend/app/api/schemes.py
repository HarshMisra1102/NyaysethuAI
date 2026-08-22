from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.scheme import (
    SchemeEligibilityRequest,
    SchemeResponse,
)


router = APIRouter(
    prefix="/schemes",
    tags=["Schemes"],
)


@router.post(
    "/eligibility",
    response_model=SchemeResponse,
)
async def check_scheme_eligibility(
    data: SchemeEligibilityRequest,
    current_user: User = Depends(get_current_user),
):
    return SchemeResponse(
        scheme_name=(
            data.scheme_name
            or "Scheme identification pending"
        ),
        eligible=None,
        confidence=None,
        explanation=(
            "AI scheme eligibility analysis will be "
            "available after AI integration."
        ),
        eligibility_conditions=[],
        missing_information=[],
        application_url=None,
        sources=[],
        disclaimer=(
            "Eligibility should be verified against "
            "the latest official government information."
        ),
    )