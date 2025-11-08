from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from transactions.schemas import OrderReadSchema
from transactions.service import order_service

orders_router = APIRouter()


@orders_router.get(
    '/', response_model=list[OrderReadSchema], summary='Получить все заказы на производство')
async def get_orders(
    session: AsyncSession = Depends(get_async_session)
) -> list[OrderReadSchema]:
    """Эндпоинт получения всех заказов на производство."""
    orders = await order_service.get_all_orders(session)
    return orders # pyright: ignore[reportReturnType]

@orders_router.get(
    '/{order_id}', response_model=OrderReadSchema, summary='Получить заказ на производство')
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> OrderReadSchema:
    """Эндпоинт получения заказа на производство."""
    order = await order_service.get_order(session, order_id)
    return order # pyright: ignore[reportReturnType]