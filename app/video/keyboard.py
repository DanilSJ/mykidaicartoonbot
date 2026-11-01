from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def duration_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="5"),
                KeyboardButton(text="15"),
            ],
        ],
        resize_keyboard=True,
    )

def generate_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сгенерировать ещё",
                                     callback_data="create_video",
                                     style="success",),
            ],
        ],
    )