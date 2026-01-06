from fastapi import Request, status
from fastapi.responses import HTMLResponse
from core.config import templates


def not_found_response(request: Request) -> HTMLResponse:
    """Возвращаем рендер шаблона 404."""
    return templates.TemplateResponse(
        request=request,
        name='404.html',
        status_code=status.HTTP_404_NOT_FOUND,
    )
