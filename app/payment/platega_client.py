import logging
from typing import Any
import aiohttp

from core.config import settings

logger = logging.getLogger(__name__)


class PlategaError(Exception):
    pass


class PlategaClient:
    def __init__(
        self,
        base_url: str = settings.PLATEGA_BASE_URL,
        merchant_id: str = settings.PLATEGA_MERCHANT_ID,
        secret: str = settings.PLATEGA_SECRET,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.merchant_id = merchant_id
        self.secret = secret

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "X-MerchantId": self.merchant_id,
            "X-Secret": self.secret,
            "Content-Type": "application/json",
        }

    async def create_transaction(
        self,
        amount: float,
        currency: str,
        description: str,
        return_url: str,
        failed_url: str,
        payload: str | None = None,
        order_id: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        payment_method: int | None = None,
    ) -> dict[str, Any]:
        # Без метода — /v2/... , с методом — /...
        url = (
            f"{self.base_url}/v2/transaction/process"
            if payment_method is None
            else f"{self.base_url}/transaction/process"
        )

        body: dict[str, Any] = {
            "paymentDetails": {"amount": amount, "currency": currency},
            "description": description,
            "return": return_url,
            "failedUrl": failed_url,
        }
        if payment_method is not None:
            body["paymentMethod"] = payment_method
        if payload is not None:
            body["payload"] = payload
        if order_id is not None:
            body["orderId"] = order_id
        if user_id is not None:
            body["metadata"] = {"userId": user_id, "userName": user_name or ""}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._headers) as resp:
                data = await resp.json(content_type=None)
                if resp.status != 200:
                    logger.error("Platega create error %s: %s", resp.status, data)
                    raise PlategaError(f"Platega {resp.status}: {data}")
                return data

    async def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/transaction/{transaction_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers) as resp:
                data = await resp.json(content_type=None)
                if resp.status != 200:
                    logger.error("Platega status error %s: %s", resp.status, data)
                    raise PlategaError(f"Platega {resp.status}: {data}")
                return data


platega_client = PlategaClient()