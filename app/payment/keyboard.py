from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dataclasses import dataclass


@dataclass(frozen=True)
class Tariff:
    duration: int
    price: float
    label: str

TARIFFS: dict[int, Tariff] = {
    1: Tariff(duration=5, price=119.0,  label="5 секунд - 119 рублей"),
    2: Tariff(duration=15, price=219.0, label="15 секунд - 219 рублей"),
}

def buy_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Купить", callback_data="buy"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def buy_request_count_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{tariff.label} — Купить",
                callback_data=f"buy_request_count_{requests}",
            )
        ]
        for requests, tariff in TARIFFS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def check_payment_keyboard(payment_id: int, payment_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=payment_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Проверить оплату",
                    callback_data=f"check_payment_{payment_id}",
                )
            ],
        ]
    )

def generate_video_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сгенерировать видео",
                                     callback_data="create_video",
                                     style="success",),
            ],
        ],
    )