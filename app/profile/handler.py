from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.utils import get_user
from core.models import db_helper, User

router = Router()

@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery):
    async with db_helper.scoped_session_dependency() as session:
        user = await get_user(session, callback.from_user.id, callback.from_user.username)

    return await callback.message.answer(f"""
    Количество рефералов: {user.referral_user_count or 0}
    Бонусы (скидка): {user.balance or 0}
    """, parse_mode="HTML")

