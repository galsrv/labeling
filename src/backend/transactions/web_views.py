from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from transactions.service import web_orders_service

web_orders_router = APIRouter()


@web_orders_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список производственных заданий',
        name='read_orders',
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


@web_orders_router.get(
        '/{order_id}',
        response_class=HTMLResponse,
        summary='Задание на производство'
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
