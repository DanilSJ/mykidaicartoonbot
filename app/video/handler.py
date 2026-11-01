import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from app.payment.keyboard import buy_keyboard
from app.utils import get_user, has_request_with_duration, delete_one_request_count
from app.video.ai import create_video
from app.video.keyboard import duration_keyboard, generate_keyboard
from app.video.state import Video
from io import BytesIO
import httpx
from core.models import db_helper, User, RequestCount, Base

router = Router()


@router.message(Command("video"))
async def cmd_video(message: Message, state: FSMContext):
    async with db_helper.scoped_session_dependency() as session:
        user = await get_user(session, message.from_user.id, message.from_user.username)

        has_5 = await has_request_with_duration(session, user.id, 5)
        has_15 = await has_request_with_duration(session, user.id, 15)

        if not has_5 and not has_15:
            return await message.answer("Вам необходимо приобрести генерации, для этого нажмите 'Купить'",
                                        reply_markup=buy_keyboard(),
                                        )

    await state.set_state(Video.image)
    return await message.answer("Для того чтобы сгенерировать видео пришлите ОДНО изображение по которому будет происходить генерация")

@router.callback_query(F.data == "create_video")
async def callback_video(callback: CallbackQuery, state: FSMContext):
    async with db_helper.scoped_session_dependency() as session:
        user = await get_user(session, callback.from_user.id, callback.from_user.username)

        has_5 = await has_request_with_duration(session, user.id, 5)
        has_15 = await has_request_with_duration(session, user.id, 15)

        if not has_5 and not has_15:
            return await callback.message.answer("Вам необходимо приобрести генерации, для этого нажмите 'Купить'",
                                        reply_markup=buy_keyboard(),
                                        )
    await state.set_state(Video.image)
    return await callback.message.answer("Для того чтобы сгенерировать видео пришлите ОДНО изображение по которому будет происходить генерация")


@router.message(Video.image, F.photo)
async def state_video_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(image_file_id=photo.file_id)
    await state.set_state(Video.duration)
    return await message.answer("Выберите длительность видео: 5 или 15 секунд👾", reply_markup=duration_keyboard())


@router.message(Video.duration, F.text)
async def state_video_duration(message: Message, state: FSMContext):
    try:
        duration = int(message.text.strip())
    except ValueError:
        return await message.answer("Выберите длительность видео: 5 или 15 секунд👾")

    if duration not in (5, 15):
        return await message.answer("Выберите длительность видео: 5 или 15 секунд👾")
    async with db_helper.scoped_session_dependency() as session:
        user = await get_user(session, message.from_user.id, message.from_user.username)

        has_5 = await has_request_with_duration(session, user.id, 5)
        has_15 = await has_request_with_duration(session, user.id, 15)

    if duration == 5:
        if not has_5:
            return await message.answer("У вас нет видео на 5 секунд выберите другую длительность👾", reply_markup=buy_keyboard())

    if duration == 15:
        if not has_15:
            return await message.answer("У вас нет видео на 15 секунд выберите другую длительность или приобретите👾", reply_markup=buy_keyboard())

    data = await state.get_data()
    await state.clear()

    await message.answer("Генерация видео займет от 3 до 5 минут, пожалуйста, подождите 🪄")

    asyncio.create_task(
        _generate_and_send(
            bot=message.bot,
            chat_id=message.chat.id,
            file_id=data["image_file_id"],
            duration=duration,
            audio=False,
            user_telegram_id=message.from_user.id,
            user_username=message.from_user.username
        )
    )


async def _generate_and_send(bot, chat_id: int, file_id: str, duration: int, audio: bool, user_telegram_id: int, user_username: str,):
    try:
        tg_file = await bot.get_file(file_id)
        buf = BytesIO()
        await bot.download_file(tg_file.file_path, destination=buf)
        buf.seek(0)

        # обход защиты seedance — накидываем сетку на изображение, изменил нейронку на minimax hailuo она не конфликтует с человеком на фото
        # grid_buf = add_grid(buf, rows=15, cols=20, line_thickness=6)

        video_url = await create_video(
            image=buf,
            duration=duration,
            audio=audio,
        )

        async with httpx.AsyncClient(timeout=120) as client:
            res = await client.get(video_url)

        if res.status_code != 200:
            return await bot.send_message(
                chat_id,
                f"Произошла ошибка при скачивании видео с ссылки {video_url}"
            )

        video_file = BufferedInputFile(
            file=res.content,
            filename="video.mp4",
        )

        await bot.send_video(
            chat_id=chat_id,
            video=video_file,
            caption="Готово! 🎬",
            supports_streaming=True,
            reply_markup=generate_keyboard()
        )

        async with db_helper.scoped_session_dependency() as session:
            user = await get_user(session, user_telegram_id, user_username)
            return await delete_one_request_count(session, user.id, duration)


    except Exception as e:
        await bot.send_message(chat_id, f"Ошибка при генерации видео: {e}")