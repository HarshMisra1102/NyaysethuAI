from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.llm import AIProviderUnavailableError
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
    try:
        response = await AIOrchestrator().process(
            message=data.problem,
            user_id=current_user.id,
        )
    except AIProviderUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
            headers={"Retry-After": "30"},
        ) from exc

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
