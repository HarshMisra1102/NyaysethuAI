from fastapi import APIRouter, Depends, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.rti import RTIDraft, RTIRequest
from app.ai.orchestrator import AIOrchestrator


router = APIRouter(
    prefix="/rti",
    tags=["RTI"],
)


@router.post(
    "/draft",
    response_model=RTIDraft,
    status_code=status.HTTP_200_OK,
)
async def generate_rti_draft(
    data: RTIRequest,
    current_user: User = Depends(get_current_user),
):
    response = await AIOrchestrator().process(
        message=data.question,
        user_id=current_user.id,
    )
    actions = "\n".join(
        f"{step.step}. {step.description}"
        for step in response.action_plan
    )

    return RTIDraft(
        department="Not determined from the available information",
        public_information_officer=None,
        subject=response.issue or "RTI information request",
        application_text=(
            f"{response.summary}\n\nSuggested next steps:\n{actions}"
        ).strip(),
        required_documents=response.required_documents,
        submission_method=None,
        submission_url=None,
        sources=[source.title for source in response.sources],
        disclaimer=response.disclaimer,
    )
