from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def buy_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Купить", callback_data="buy"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def buy_request_count_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="10", callback_data="buy_request_count_10"),
        ],
        [
            InlineKeyboardButton(text="15", callback_data="buy_request_count_15"),
        ],
        [
            InlineKeyboardButton(text="20", callback_data="buy_request_count_20"),
        ],
        [
            InlineKeyboardButton(text="30", callback_data="buy_request_count_30"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
