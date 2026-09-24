from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User



async def get_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
) -> Any:
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
