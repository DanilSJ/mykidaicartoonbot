from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dataclasses import dataclass


@dataclass(frozen=True)
class Tariff:
    requests: int
    price: float
    label: str


# Тарифы: количество генераций -> цена
TARIFFS: dict[int, Tariff] = {
    10: Tariff(requests=10, price=99.0,  label="10 генераций"),
    15: Tariff(requests=15, price=139.0, label="15 генераций"),
    20: Tariff(requests=20, price=179.0, label="20 генераций"),
    30: Tariff(requests=30, price=249.0, label="30 генераций"),
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
                text=f"{tariff.label} — {tariff.price:.0f} ₽",
                callback_data=f"buy_request_count_{requests}",
            )
        ]
        for requests, tariff in TARIFFS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def check_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Проверить оплату",
                    callback_data=f"check_payment_{payment_id}",
                )
            ],
        ]
    )