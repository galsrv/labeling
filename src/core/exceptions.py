from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.log import logger
from core.config import settings as s, templates
from auth.exceptions import BaseAuthException
from database.exceptions import BaseDBException, ObjectNotFound


def _html_not_found_response(request: Request) -> HTMLResponse:
    """Возвращаем рендер шаблона 404."""
    return templates.TemplateResponse(
        request=request,
        name='404.html',
        status_code=status.HTTP_404_NOT_FOUND,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрируем исключения для всех FastAPI-функций."""

    @app.exception_handler(BaseDBException)
    async def db_operation_failure(request: Request, exc: BaseDBException) -> JSONResponse | RedirectResponse:
        """Обработчик исключений, возникших при операциях с БД.

        Возращаем JSON/HTML в зависимости от url в запросе web/api.
        Для ошибок вида ObjectNotModified возвращаем JSON, обработка на стороне фронтенда, отдельного шаблона на это нет.
        """
        logger.info(s.MESSAGE_ERROR_PROCESSING_REQUEST.format(url=str(request.url), error=str(exc)))

        if isinstance(exc, ObjectNotFound):
            if request.url.path.startswith(s.HTML_URL_PREFIX):
                return _html_not_found_response(request)

            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={'detail': str(exc)},
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={'detail': str(exc)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse | RedirectResponse:
        """Обработчик исключений, возниквших при попытке разобрать URL запроса - не нашелся роутер для пути."""
        # Chrome что-то запрашивает и гадит в логах. Так убираем кастомный лог, остается только лог Uvicorn
        if request.url.path == '/.well-known/appspecific/com.chrome.devtools.json':
            return await http_exception_handler(request, exc)

        logger.info(s.MESSAGE_ERROR_PROCESSING_REQUEST.format(url=str(request.url), error=str(exc)))

        if exc.status_code in (
            status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_CONTENT
        ) and request.url.path.startswith(s.HTML_URL_PREFIX):
            return _html_not_found_response(request)

        # Для пользователей API оставляем дефолтное поведение FastAPI
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Обработчик исключений, возниквших при конвертации путей - например /web/orders/abcde."""
        logger.info(s.MESSAGE_ERROR_PROCESSING_REQUEST.format(url=str(request.url), error=str(exc)))

        if request.url.path.startswith(s.HTML_URL_PREFIX):
            return _html_not_found_response(request)

        # Для пользователей API оставляем дефолтное поведение FastAPI
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(BaseAuthException)
    async def invalid_credentials(request: Request, exc: BaseAuthException) -> JSONResponse:
        """Обработчик исключений для неуспешной аутентификации пользователя."""
        logger.info(s.MESSAGE_ERROR_PROCESSING_REQUEST.format(url=str(request.url), error=str(exc)))

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': str(exc)},
        )
