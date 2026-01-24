from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from items.service import web_items_service

web_items_router = APIRouter()


@web_items_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список весов',
        name='web_get_all_items',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_items(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список продуктов."""
    all_items = await web_items_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='items.html',
        context={'all_items': all_items}
    )
