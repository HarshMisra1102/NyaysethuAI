from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
)


async def register_user(
    db: AsyncSession,
    data: RegisterRequest,
) -> User:

    result = await db.execute(
        select(User).where(
            User.email == data.email.lower()
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError(
            "An account with this email already exists."
        )

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        state=data.state,
        district=data.district,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    data: LoginRequest,
) -> User | None:

    result = await db.execute(
        select(User).where(
            User.email == data.email.lower()
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(
        data.password,
        user.password_hash,
    ):
        return None

    return user


def generate_token(user: User) -> str:
    return create_access_token(user.id)