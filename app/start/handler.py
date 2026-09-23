from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.utils import get_user
from core.models import db_helper

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        await get_user(session, message.from_user.id, message.from_user.username)
        return await message.answer("Привет, в этом боте ты можешь сгенерировать видео по картинке")