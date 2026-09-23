import asyncio
import time
from io import BytesIO
from arkruntime import AsyncArk

from app.video.image import _to_data_uri
from core.config import settings

client = AsyncArk(
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3",
    api_key=settings.AI_API_KEY,
)


async def create_video(prompt: str, image: BytesIO, duration: int = 4, audio: bool = False) -> str:
    """
    Асинхронно создаёт видео и возвращает ссылку на готовый файл.

    :param prompt: текстовый сценарий
    :param image: BytesIO с изображением (jpeg/png/webp)
    :param duration: длительность в секундах
    :param audio: генерация аудио
    """
    image.seek(0)
    image_bytes = image.read()

    if image_bytes.startswith(b"\x89PNG"):
        mime = "image/png"
    elif image_bytes[:3] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    data_uri = _to_data_uri(image_bytes, mime=mime)

    create_result = await client.content_generation.tasks.create(
        model="dreamina-seedance-2-5-260628",
        content=[
            {"type": "text", "text": f"{prompt}. Убери белую сетку на изображении"},
            {
                "type": "image_url",
                "image_url": {"url": data_uri},
                "role": "reference_image",
            },
        ],
        generate_audio=audio,
        ratio="16:9",
        duration=duration,
        extra_body={
            "omni_reference_task_type": "reference",
            "output_format": "mp4",
        },
    )
    task_id = create_result.id

    deadline = time.monotonic() + 30 * 60
    while time.monotonic() < deadline:
        get_result = await client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            return get_result.content.video_url
        elif status == "failed":
            raise RuntimeError(f"Video generation task failed: {get_result.error}")

        await asyncio.sleep(10)

    raise TimeoutError("Task did not finish in 30 minutes")