from fastapi import Request

from core.log import logger


def logging_dependency(request: Request) -> None:
    """Логируем обращение к эндпоинту."""
    logger.info(f'Обращение {request.method}:{request.url}')
