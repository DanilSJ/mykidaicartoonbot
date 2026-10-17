import asyncio
import base64
import time
from io import BytesIO
import requests

from core.config import settings

API_URL = "https://api.magnific.com/v1/ai/video/minimax-h3-768p"

HEADERS = {
    "x-magnific-api-key": settings.AI_API_KEY,
    "Content-Type": "application/json",
}


def _get_image_mime(image_bytes: bytes) -> str:
    """Определяет MIME-тип изображения по сигнатуре файла."""
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    if (
        image_bytes.startswith(b"RIFF")
        and image_bytes[8:12] == b"WEBP"
    ):
        return "image/webp"

    raise ValueError("Неподдерживаемый формат изображения")


def _create_video_task(
    prompt: str,
    image_bytes: bytes,
    duration: int,
) -> str:
    """Создаёт задачу генерации видео в Magnific AI."""
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "prompt": f"{prompt}. Убери белую сетку на изображении",
        "image": image_base64,
        "duration": duration,
        "aspect_ratio": "adaptive",
        "aigc_watermark": False,
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=HEADERS,
        timeout=60,
    )
    response.json()

    result = response.json()
    data = result.get("data", {})

    task_id = data.get("task_id")

    if not task_id:
        raise RuntimeError(
            f"Magnific не вернул task_id: {result}"
        )

    return task_id


def _get_video_task(task_id: str) -> dict:
    """Получает состояние задачи генерации видео."""
    response = requests.get(
        f"{API_URL}/{task_id}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json()
    data = result.get("data", {})

    if not data:
        raise RuntimeError(
            f"Некорректный ответ Magnific: {result}"
        )

    return data


async def create_video(
    prompt: str,
    image: BytesIO,
    duration: int = 5,
    audio: bool = False,
) -> str:
    """
    Асинхронно создаёт видео через Magnific AI
    и возвращает ссылку на готовый файл.

    :param prompt: текстовый сценарий видео
    :param image: BytesIO с изображением JPEG, PNG или WEBP
    :param duration: длительность видео в секундах
    :param audio: оставлен для совместимости; API-пример
                  Magnific не содержит параметра генерации аудио
    :return: URL готового видео
    """
    if duration <= 0:
        raise ValueError("Длительность видео должна быть положительной")

    image.seek(0)
    image_bytes = image.read()

    if not image_bytes:
        raise ValueError("Передано пустое изображение")

    _get_image_mime(image_bytes)

    # Создание задачи не блокирует event loop.
    task_id = await asyncio.to_thread(
        _create_video_task,
        prompt,
        image_bytes,
        duration,
    )

    deadline = time.monotonic() + 30 * 60

    while time.monotonic() < deadline:
        data = await asyncio.to_thread(
            _get_video_task,
            task_id,
        )

        status = str(data.get("status", "")).upper()

        if status in {"SUCCEEDED", "SUCCESS", "COMPLETED"}:
            generated = data.get("generated") or []

            # Проверяем возможные форматы ответа API.
            for item in generated:
                if isinstance(item, str) and item.startswith("http"):
                    return item

                if isinstance(item, dict):
                    url = (
                        item.get("url")
                        or item.get("video_url")
                        or item.get("download_url")
                    )
                    if url:
                        return url

            for key in ("video_url", "url", "result_url"):
                if data.get(key):
                    return data[key]

            raise RuntimeError(
                f"Видео готово, но ссылка отсутствует: {data}"
            )

        if status in {"FAILED", "ERROR", "CANCELLED"}:
            raise RuntimeError(
                f"Генерация видео завершилась ошибкой: {data}"
            )

        await asyncio.sleep(10)

    raise TimeoutError(
        f"Magnific не завершил генерацию за 30 минут. "
        f"Task ID: {task_id}"
    )