from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.rights import (
    RightsRequest,
    RightsResponse,
    RightItem,
)
from app.ai.orchestrator import AIOrchestrator


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
    response = await AIOrchestrator().process(
        message=data.problem,
        user_id=current_user.id,
    )

    return RightsResponse(
        category=data.category or response.category or "RIGHTS",
        summary=response.summary,
        rights=[
            RightItem(title=item, explanation=item)
            for item in response.possible_rights
        ],
        action_plan=[step.description for step in response.action_plan],
        required_documents=response.required_documents,
        sources=[source.title for source in response.sources],
        disclaimer=response.disclaimer,
    )
