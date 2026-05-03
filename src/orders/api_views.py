from fastapi import APIRouter, Cookie, Depends, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import is_orders_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from frontend.responses import JsonToFrontendResponse
from orders.schemas import OrderPageSchema, OrderReadSchema
from orders.service import orders_service

api_orders_router = APIRouter()


@api_orders_router.get(
    '/',
    response_model=OrderPageSchema,
    summary='Получить список заказов на производство',
    dependencies=[Depends(is_orders_view_permitted), Depends(logging_dependency)],
)
async def get_orders(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(
        ge=1,
        default=1),
    size: int = Query(
        ge=s.PAGINATION_MIN_SIZE,
        le=s.PAGINATION_MAX_SIZE,
        default=s.PAGINATION_DEFAULT_PAGE_SIZE),
) -> OrderPageSchema:
    """Эндпоинт получения списка заказов на производство."""
    orders = await orders_service.get_page(session, page, size)
    return orders


@api_orders_router.get(
    '/{order_id}',
    response_model=OrderReadSchema,
    summary='Получить заказ на производство',
    dependencies=[Depends(is_orders_view_permitted), Depends(logging_dependency)],
)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> OrderReadSchema:
    """Эндпоинт получения заказа на производство."""
    order = await orders_service.get_order(session, order_id)
    return order


@api_orders_router.post(
        '/{order_id}/sgtin_batch_print',
        response_model=JsonToFrontendResponse,
        name='web_orders_sgtin_batch_print',
        summary='Пакетная печать кодов',
        dependencies=[Depends(is_orders_view_permitted), Depends(logging_dependency)],
)
async def web_orders_sgtin_batch_print(
    order_id: int,
    number_to_print: int = Form(),
    workplace_id: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_async_session),
) -> JsonToFrontendResponse:
    """Печатаем коды маркировки."""
    return await orders_service.batch_print(order_id, number_to_print, workplace_id, session)
