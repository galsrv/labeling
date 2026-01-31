from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from workplaces.service import web_workplaces_service

web_workplaces_router = APIRouter()


@web_workplaces_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список рабочих мест',
        name='web_get_all_workplaces',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_workplaces(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список рабочих мест."""
    all_workplaces = await web_workplaces_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='workplaces.html',
        context={'all_workplaces': all_workplaces}
    )
