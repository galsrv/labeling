from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from core.config import templates

html_root_router = APIRouter()


@html_root_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Корневая страница сайта',
        name='site_root',
)
async def site_root(
    request: Request,
) -> HTMLResponse:
    """Направляем на приветственную страницу."""
    return templates.TemplateResponse(
        request=request,
        name='index.html',
    )
