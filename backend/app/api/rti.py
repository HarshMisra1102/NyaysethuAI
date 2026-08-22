from fastapi import APIRouter, Depends, status

from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.rti import RTIDraft, RTIRequest


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
    return RTIDraft(
        department="AI department identification pending",
        public_information_officer=None,
        subject="RTI Application",
        application_text=(
            "AI-generated RTI application will be "
            "provided after AI integration."
        ),
        required_documents=[],
        submission_method=None,
        submission_url=None,
        sources=[],
        disclaimer=(
            "This draft is for informational purposes "
            "and should be verified before submission."
        ),
    )