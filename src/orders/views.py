from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from frontend.responses import WebJsonResponse
from orders.service import web_orders_service

orders_router = APIRouter()


@orders_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список производственных заданий',
        name='read_orders',
        dependencies=[Depends(logging_dependency)]
)
async def read_orders(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список производственных заданий."""
    orders = await web_orders_service.list_orders(session)
    return templates.TemplateResponse(
        request=request,
        name='orders.html',
        context={'orders': orders}
    )


@orders_router.post(
        '/{order_id}/sgtin_batch_print',
        response_model=WebJsonResponse,
        name='web_orders_sgtin_batch_print',
        summary='Пакетная печать кодов',
        dependencies=[Depends(logging_dependency)]
)
async def web_orders_sgtin_batch_print(
    order_id: int,
    number_to_print: int = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> WebJsonResponse:
    """Печатаем коды маркировки."""
    if not 1 <= number_to_print <= 1000:
        return WebJsonResponse(ok=False, message='Количество для печати должно быть в диапазоне 1-1000')

    return await web_orders_service.batch_print(order_id, number_to_print, session)


@orders_router.get(
        '/{order_id}',
        response_class=HTMLResponse,
        summary='Задание на производство',
        dependencies=[Depends(logging_dependency)]
)
async def execute_order(
    order_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем интерфейс производственного задания."""
    order = await web_orders_service.get_order(session, order_id)
    return templates.TemplateResponse(
        request=request,
        name='order_execution.html',
        context={'order': order}
    )
