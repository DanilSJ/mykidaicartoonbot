import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app import start_router, video_router
from core.config import settings


async def main():
    bot = Bot(
        token=settings.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_routers(start_router, video_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
