from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from transactions.schemas import OrderReadSchema
from transactions.service import api_orders_service

api_orders_router = APIRouter()


@api_orders_router.get(
    '/', response_model=list[OrderReadSchema], summary='Получить все заказы на производство')
async def get_orders(
    session: AsyncSession = Depends(get_async_session)
) -> list[OrderReadSchema]:
    """Эндпоинт получения всех заказов на производство."""
    orders = await api_orders_service.list_orders(session)
    return orders


@api_orders_router.get(
    '/{order_id}', response_model=OrderReadSchema, summary='Получить заказ на производство')
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> OrderReadSchema:
    """Эндпоинт получения заказа на производство."""
    order = await api_orders_service.get_order(session, order_id)
    return order
