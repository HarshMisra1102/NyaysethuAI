from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.case_service import get_case
from app.services.chat_service import (
    get_or_create_conversation,
    save_message,
)
from app.services.ai_servies import AIService
from app.ai.orchestrator import AIOrchestrator


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

    # --------------------------------------------------
    # 1. Validate case
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 2. Get or create conversation
    # --------------------------------------------------

    conversation = await get_or_create_conversation(
        db,
        case,
    )

    # --------------------------------------------------
    # 3. Save user message
    # --------------------------------------------------

    await save_message(
        db,
        conversation.id,
        "user",
        data.message,
    )

    # --------------------------------------------------
    # 4. Run AI
    # --------------------------------------------------

    try:

        ai_service = AIService(
            orchestrator=AIOrchestrator()
        )

        ai_response = await ai_service.process_query(
            request=data,
            user_id=current_user.id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "AI processing failed. "
                "Please try again."
            ),
        ) from exc

    # --------------------------------------------------
    # 5. Save assistant response
    # --------------------------------------------------

    assistant_message = await save_message(
        db,
        conversation.id,
        "assistant",
        ai_response.summary,
    )

    # --------------------------------------------------
    # 6. Return final response
    # --------------------------------------------------

    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        response=ai_response,
        created_at=datetime.now(timezone.utc),
    )