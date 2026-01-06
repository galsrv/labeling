from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from frontend.responses import not_found_response


class ObjectNotFound(Exception):
    """Исключение - Объект не найден."""
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрируем исключения для всех FastAPI-функций."""

    @app.exception_handler(ObjectNotFound)
    async def object_not_found_html(request: Request, exc: ObjectNotFound) -> JSONResponse | RedirectResponse:
        """Возращаем JSON/HTML в зависимости от того, откуда был запрос к ненайденного объекту."""
        if request.headers.get('accept', '').startswith('text/html'):
            return not_found_response(request)

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'detail': str(exc)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse | RedirectResponse:
        # Кастомизируем поведение для ненайденных страниц для пользователей фронтенда
        if exc.status_code in (
            status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_CONTENT
        ) and request.url.path.startswith('/web'):
            return not_found_response(request)

        # Для пользователей API поведение оставляем дефолтное
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def custom_http_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse | RedirectResponse:
        # Кастомизируем поведение для ошибок конвертации путей на фронтенде - например /web/orders/abcde
        if request.url.path.startswith('/web'):
            return not_found_response(request)

        # Для пользователей API поведение оставляем дефолтное
        return await http_exception_handler(request, exc)
