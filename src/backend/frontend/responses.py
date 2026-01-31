from fastapi import Request, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from core.config import templates


def not_found_response(request: Request) -> HTMLResponse:
    """Возвращаем рендер шаблона 404."""
    return templates.TemplateResponse(
        request=request,
        name='404.html',
        status_code=status.HTTP_404_NOT_FOUND,
    )


class WebJsonResponse(BaseModel):
    """Структура ответа фронтенду в формате JSON."""
    ok: bool
    message: str
    data: str | None = None
