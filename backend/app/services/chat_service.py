from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.models.conversation import Conversation
from app.models.message import Message


async def get_or_create_conversation(
    db: AsyncSession,
    case: Case,
) -> Conversation:

    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.case_id == case.id
        )
        .order_by(
            Conversation.created_at.asc()
        )
        .limit(1)
    )

    conversation = result.scalar_one_or_none()

    if conversation:
        return conversation

    conversation = Conversation(
        case_id=case.id,
    )

    db.add(conversation)

    await db.commit()
    await db.refresh(conversation)

    return conversation


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    await db.commit()
    await db.refresh(message)

    return message


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: int,
) -> list[Message]:

    result = await db.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
    )

    return list(result.scalars().all())