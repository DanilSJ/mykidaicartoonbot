from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from app.start.keyboard import start_keyboard
from app.utils import get_user
from core.models import db_helper

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with db_helper.scoped_session_dependency() as session:
        await get_user(session, message.from_user.id, message.from_user.username)
        video = FSInputFile("media/start.MOV")
        return await message.answer_video(video=video, caption="""🎬 Добро пожаловать в Kidai!

Представь: ты нарисовал героя, а он вдруг ожил! ✨

Теперь ты можешь сам создавать мультфильмы из своих картинок.

🎨 Загрузи рисунок.

🎥 Запусти волшебство.

🌈 Получи собственное видео.

👇 Начни своё приключение!""", parse_mode="HTML", reply_markup=start_keyboard())
