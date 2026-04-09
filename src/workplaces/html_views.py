from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from core.config import templates
from core.dependencies import logging_dependency

html_workplaces_router = APIRouter()


@html_workplaces_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список рабочих мест',
        name='web_get_all_workplaces',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_workplaces(
    request: Request,
) -> HTMLResponse:
    """Отображаем список рабочих мест."""
    return templates.TemplateResponse(
        request=request,
        name='workplaces.html',
    )
