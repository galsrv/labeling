from typing import TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from transactions.repository import orders_repo
from transactions.schemas import OrderReadSchema, OrderWebSchema

T = TypeVar('T', bound=BaseModel)


class OrdersService:
    """Сервисный слой для производственный заданий."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def list_orders(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все задания."""
        orders = await orders_repo.get_all(session)
        orders_dto = [self.read_model.model_validate(order) for order in orders]
        return orders_dto

    async def get_order(self, session: AsyncSession, order_id: int) -> T:
        """Возвращаем из БД задание по его id."""
        order = await orders_repo.get(session, order_id)

        if order is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        order_dto = self.read_model.model_validate(order)
        return order_dto


api_orders_service = OrdersService(read_model=OrderReadSchema)

web_orders_service = OrdersService(read_model=OrderWebSchema)
