from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class ObjectNotFound(Exception):
    """Исклчюение - Объект не найден."""
    pass


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрируем исключения для всех FastAPI-функций."""

    @app.exception_handler(ObjectNotFound)
    async def object_not_found_handler(
        request: Request,
        exc: ObjectNotFound,
    ) -> JSONResponse:
        """Обрабаотываем исключение Объект не найден."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    # @app.exception_handler(ObjectNotFound)
    # async def object_not_found_html(request: Request, exc: ObjectNotFound):
    #     if request.headers.get("accept", "").startswith("text/html"):
    #         return templates.TemplateResponse(
    #             "404.html",
    #             {"request": request, "detail": str(exc)},
    #             status_code=404,
    #         )
    #     return JSONResponse(
    #         status_code=404,
    #         content={"detail": str(exc)},
    #     )
