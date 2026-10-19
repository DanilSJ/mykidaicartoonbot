from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Создать видео",
                    callback_data=f"create_video",
                    style="success"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Политика конфиденциальности",
                    callback_data=f"privacy_police",
                    style="primary"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Пользовательское соглашение",
                    callback_data=f"user_police",
                    style="primary"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Техподдержка",
                    callback_data=f"support_contact",
                    style="primary"
                )
            ],
        ]
    )