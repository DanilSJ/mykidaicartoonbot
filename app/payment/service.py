import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.payment.keyboard import TARIFFS
from app.payment.platega_client import PlategaError, platega_client
from core.models import Payment, User, RequestCount

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_payment(
        self,
        user: User,
        requests_count: int,
        amount: float,
    ) -> Payment:
        tariff = TARIFFS.get(requests_count)
        if tariff is None:
            raise ValueError(f"Неизвестный тариф: {requests_count}")

        payment = Payment(
            duration=tariff.duration,
            status="PENDING",
            amount=amount,
            currency="RUB",
            user_id=user.id,
        )
        self.session.add(payment)
        await self.session.flush()  # получаем payment.id

        try:
            result = await platega_client.create_transaction(
                amount=amount,
                currency="RUB",
                description=f"Покупка {tariff.label}",
                return_url="PAYMENT_RETURN_URL",
                failed_url="PAYMENT_FAILED_URL",
                payload=f"payment_id={payment.id}",
                order_id=str(payment.id),
                user_id=str(user.telegram_id),
                user_name=user.username or "",
                payment_method=None,  # пользователь сам выберет способ
            )
        except PlategaError:
            payment.status = "CANCELED"
            await self.session.commit()
            raise

        payment.transaction_id = result.get("transactionId")
        payment.payment_url = result.get("url") or result.get("redirect")

        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_payment(self, payment_id: int) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def sync_payment_status(self, payment: Payment) -> str:
        """
        Проверяет статус в Platega и обновляет БД.
        При первом CONFIRMED — начисляет генерации.
        Возвращает актуальный статус.
        """
        if not payment.transaction_id:
            return payment.status

        try:
            data = await platega_client.get_transaction(payment.transaction_id)
        except PlategaError:
            logger.exception("Не удалось получить статус платежа %s", payment.id)
            return payment.status

        new_status = data.get("status", payment.status)

        if new_status == payment.status:
            return payment.status

        # Начисляем только при первом переходе в CONFIRMED
        if new_status == "CONFIRMED" and payment.status != "CONFIRMED":
            request_row = RequestCount(
                duration=payment.duration,
                user_id=payment.user_id,
            )
            self.session.add(request_row)

            query = select(User).where(User.id == payment.user_id)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()

            if user:
                if user.connect_referral_user:
                    query = select(User).where(User.telegram_id == user.connect_referral_user)
                    result = await self.session.execute(query)
                    user_referral = result.scalar_one_or_none()

                    if user_referral:
                        user_referral.balance = user_referral.balance + 15

        payment.status = new_status
        await self.session.commit()
        return new_status