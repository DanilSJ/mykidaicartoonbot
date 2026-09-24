# app/payment/handlers.py

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from app.payment.keyboard import buy_request_count_keyboard, check_payment_keyboard, TARIFFS
from app.payment.service import PaymentService
from app.utils import get_user
from core.models import db_helper

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "buy")
async def btn_buy(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите количество генераций, которое хотите купить:",
        reply_markup=buy_request_count_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_request_count_"))
async def btn_buy_request_count(callback: CallbackQuery):
    requests_count = int(callback.data.rsplit("_", 1)[-1])
    tariff = TARIFFS.get(requests_count)
    if tariff is None:
        await callback.answer("Неизвестный тариф", show_alert=True)
        return

    await callback.answer()

    async with db_helper.scoped_session_dependency() as session:
        user = await get_user(
            session, callback.from_user.id, callback.from_user.username
        )
        service = PaymentService(session)

        try:
            payment = await service.create_payment(user, requests_count)
        except Exception:
            logger.exception("Ошибка создания платежа")
            await callback.message.answer("Не удалось создать платёж. Попробуйте позже.")
            return

        await callback.message.answer(
            f"💳 <b>{tariff.label}</b>\n"
            f"Сумма: <b>{tariff.price:.0f} ₽</b>\n\n"
            f"Оплатите по ссылке:\n{payment.payment_url}\n\n"
            f"После оплаты нажмите «Проверить оплату».",
            reply_markup=check_payment_keyboard(payment.id),
            disable_web_page_preview=True,
        )


@router.callback_query(F.data.startswith("check_payment_"))
async def btn_check_payment(callback: CallbackQuery):
    payment_id = int(callback.data.rsplit("_", 1)[-1])

    async with db_helper.scoped_session_dependency() as session:
        service = PaymentService(session)

        payment = await service.get_payment(payment_id)
        if payment is None:
            await callback.answer("Платёж не найден", show_alert=True)
            return

        # уже подтверждён — не дёргаем API
        if payment.status == "CONFIRMED":
            await callback.answer("Оплата уже подтверждена ✅", show_alert=True)
            return

        if payment.status in ("CANCELED", "CHARGEBACKED"):
            await callback.answer("Платёж отменён ❌", show_alert=True)
            return

        status = await service.sync_payment_status(payment)

        if status == "CONFIRMED":
            await callback.message.edit_text(
                f"✅ Оплата получена!\n"
                f"Начислено <b>{payment.request_count}</b> генераций."
            )
            await callback.answer("Готово!")
        elif status in ("CANCELED", "CHARGEBACKED"):
            await callback.message.edit_text("❌ Платёж отклонён.")
            await callback.answer()
        else:
            await callback.answer(
                "⏳ Оплата ещё не поступила. Попробуйте через минуту.",
                show_alert=True,
            )