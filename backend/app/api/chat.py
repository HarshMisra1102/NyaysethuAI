from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ActionStep,
    ChatAIResponse,
    ChatRequest,
    ChatResponse,
)
from app.services.case_service import get_case
from app.services.chat_service import (
    get_or_create_conversation,
    save_message,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/query",
    response_model=ChatResponse,
)
async def process_chat_query(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.case_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="case_id is required.",
        )

    case = await get_case(
        db,
        data.case_id,
        current_user.id,
    )

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    conversation = await get_or_create_conversation(
        db,
        case,
    )

    await save_message(
        db,
        conversation.id,
        "user",
        data.message,
    )

    # AI integration will be added in a later step.
    ai_response = ChatAIResponse(
        issue=case.title,
        category=case.category,
        summary="AI processing is not connected yet.",
        possible_rights=[],
        evidence=[],
        action_plan=[
            ActionStep(
                step=1,
                title="AI processing pending",
                description=(
                    "The AI service will analyze this "
                    "query after integration."
                ),
            )
        ],
        required_documents=[],
        sources=[],
        disclaimer=(
            "This system provides informational civic "
            "and legal guidance and is not a substitute "
            "for professional legal advice."
        ),
    )

    assistant_message = await save_message(
        db,
        conversation.id,
        "assistant",
        ai_response.summary,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        response=ai_response,
        created_at=datetime.now(timezone.utc),
    )