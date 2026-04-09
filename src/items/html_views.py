from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_items_router = APIRouter()


@html_items_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список продуктов',
        name='web_get_all_items',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_items(
    request: Request,
) -> HTMLResponse:
    """Отображаем список продуктов."""
    return templates.TemplateResponse(
        request=request,
        name='items.html',
    )
