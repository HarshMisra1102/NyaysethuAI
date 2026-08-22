from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate


async def create_case(
    db: AsyncSession,
    user_id: int,
    data: CaseCreate,
) -> Case:

    case = Case(
        user_id=user_id,
        title=data.title.strip(),
        category=data.category.upper(),
        description=data.description.strip(),
        status="OPEN",
    )

    db.add(case)

    await db.commit()
    await db.refresh(case)

    return case


async def get_user_cases(
    db: AsyncSession,
    user_id: int,
) -> list[Case]:

    result = await db.execute(
        select(Case)
        .where(Case.user_id == user_id)
        .order_by(Case.created_at.desc())
    )

    return list(result.scalars().all())


async def get_case(
    db: AsyncSession,
    case_id: int,
    user_id: int,
) -> Case | None:

    result = await db.execute(
        select(Case).where(
            Case.id == case_id,
            Case.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()


async def update_case(
    db: AsyncSession,
    case: Case,
    data: CaseUpdate,
) -> Case:

    updates = data.model_dump(
        exclude_unset=True,
    )

    if "title" in updates and updates["title"]:
        case.title = updates["title"].strip()

    if "category" in updates and updates["category"]:
        case.category = updates["category"].upper()

    if "description" in updates and updates["description"]:
        case.description = updates["description"].strip()

    if "status" in updates and updates["status"]:
        case.status = updates["status"].upper()

    await db.commit()
    await db.refresh(case)

    return case


async def delete_case(
    db: AsyncSession,
    case: Case,
) -> None:

    await db.delete(case)
    await db.commit()