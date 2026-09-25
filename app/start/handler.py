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

        text = (
            "🎬 <b>Добро пожаловать в KidaiCartoon</b>\n\n"
            "✨ <b>Оживи свои идеи</b> — превращай статичные изображения "
            "в впечатляющие видеоролики за считанные секунды!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 <b>Что я умею:</b>\n\n"
            "🖼 <b>Генерация видео</b> — превращаю любую картинку в живое видео\n"
            "🎨 <b>Качественный результат</b> — современные AI-технологии\n"
            "⚡ <b>Быстро и просто</b> — загрузи фото и получи видео\n"
            "💾 <b>Удобно</b> — скачивай результат в один клик\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>Как начать:</b>\n"
            "Напишите /video"
        )

        return await message.answer(text, parse_mode="HTML")
