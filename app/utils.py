from typing import Any
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.models import User, RequestCount


async def get_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    referrer_id: int | None = None,
) -> Any:
    query = (
        select(User)
        .where(User.telegram_id == telegram_id)
        .options(selectinload(User.requests_count))
    )
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return user

    referrer_user_id = None
    if referrer_id:
        query = select(User).where(User.telegram_id == referrer_id)
        result = await session.execute(query)
        referrer_user = result.scalar_one_or_none()

        if referrer_user:
            referrer_user_id = referrer_user.telegram_id
            if not referrer_user.referral_user_count:
                referrer_user.referral_user_count = 1

            referrer_user.referral_user_count = referrer_user.referral_user_count + 1

            if referrer_user.referral_user_count == 3:
                request_row = RequestCount(
                    duration=5,
                    user_id=referrer_user.id,
                )
                session.add(request_row)

    user = User(
        telegram_id=telegram_id,
        username=username,
        connect_referral_user=referrer_user_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

async def has_request_with_duration(session, user_id: int, duration: int) -> bool:
    query = select(
        exists().where(
            RequestCount.user_id == user_id,
            RequestCount.duration == duration,
        )
    )
    result = await session.execute(query)
    return result.scalar()