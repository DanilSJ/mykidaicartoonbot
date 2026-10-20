from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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

def generate_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Сгенерировать ещё", style="success"),
            ],
        ],
        resize_keyboard=True,
    )