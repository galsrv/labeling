from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse


web_root_router = APIRouter()


@web_root_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Корневая страница сайта',
        name='site_root',
)
async def site_root(
    request: Request,
) -> RedirectResponse:
    """Переадресуем на страницу с производственными заданиями."""
    url = request.url_for('read_orders')
    return RedirectResponse(url=url)
