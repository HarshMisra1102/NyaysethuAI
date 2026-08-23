from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.scheme import (
    SchemeEligibilityRequest,
    SchemeResponse,
)
from app.ai.orchestrator import AIOrchestrator


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
    details = [
        f"Scheme: {data.scheme_name}" if data.scheme_name else None,
        f"Age: {data.age}" if data.age is not None else None,
        f"State: {data.state}" if data.state else None,
        f"District: {data.district}" if data.district else None,
        f"Occupation: {data.occupation}" if data.occupation else None,
        f"Annual income: {data.annual_income}" if data.annual_income is not None else None,
        f"Category: {data.category}" if data.category else None,
    ]
    query = "Please assess government scheme eligibility.\n" + "\n".join(
        detail for detail in details if detail
    )
    response = await AIOrchestrator().process(
        message=query,
        user_id=current_user.id,
    )

    return SchemeResponse(
        scheme_name=data.scheme_name or response.issue or "Relevant scheme",
        eligible=None,
        confidence=None,
        explanation=response.summary,
        eligibility_conditions=response.possible_rights,
        missing_information=response.required_documents,
        application_url=None,
        sources=[source.title for source in response.sources],
        disclaimer=response.disclaimer,
    )
