from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    CaseUpdate,
)
from app.services.case_service import (
    create_case,
    delete_case,
    get_case,
    get_user_cases,
    update_case,
)


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_case(
    data: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_case(
        db,
        current_user.id,
        data,
    )


@router.get(
    "",
    response_model=list[CaseResponse],
)
async def list_cases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_user_cases(
        db,
        current_user.id,
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
async def get_single_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await get_case(
        db,
        case_id,
        current_user.id,
    )

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case


@router.patch(
    "/{case_id}",
    response_model=CaseResponse,
)
async def update_existing_case(
    case_id: int,
    data: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await get_case(
        db,
        case_id,
        current_user.id,
    )

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return await update_case(
        db,
        case,
        data,
    )


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case = await get_case(
        db,
        case_id,
        current_user.id,
    )

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    await delete_case(
        db,
        case,
    )