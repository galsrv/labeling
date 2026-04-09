from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_orders_router = APIRouter()


@html_orders_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список производственных заданий',
        name='read_orders',
        dependencies=[Depends(logging_dependency)]
)
async def read_orders(
    request: Request,
) -> HTMLResponse:
    """Отображаем список производственных заданий."""
    return templates.TemplateResponse(
        request=request,
        name='orders.html',
    )


@html_orders_router.get(
        '/{order_id}',
        response_class=HTMLResponse,
        summary='Задание на производство',
        dependencies=[Depends(logging_dependency)]
)
async def read_order(
    order_id: int,
    request: Request,
) -> HTMLResponse:
    """Отображаем интерфейс производственного задания."""
    return templates.TemplateResponse(
        request=request,
        name='order_execution.html',
    )
