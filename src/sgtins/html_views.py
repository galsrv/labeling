from fastapi import APIRouter, Depends, Request

from fastapi.responses import HTMLResponse

from core.dependencies import logging_dependency
from core.config import templates


html_sgtin_router = APIRouter()


@html_sgtin_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Базовый интерфейс кодов маркировки',
        name='read_sgtins',
        dependencies=[Depends(logging_dependency)]
)
async def web_read_sgtins(
    request: Request,
) -> HTMLResponse:
    """Базовый интерфейс кодов маркировки."""
    return templates.TemplateResponse(
        request=request,
        name='sgtins.html'
    )
