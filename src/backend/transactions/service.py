from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.config import settings as s
from transactions.models import OrderOrm


class OrderService(BaseService):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(OrderOrm)

    async def get_all_orders(
        self,
        session: AsyncSession,
    ) -> list[OrderOrm]:
        """Получаем все заказы на производство."""
        orders = await self.get_all(session)
        return orders

    async def get_order(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> OrderOrm:
        """Получаем продукт."""
        order: OrderOrm | None = await self.get(session, order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        return order


order_service = OrderService()
