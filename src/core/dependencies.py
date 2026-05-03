from fastapi import Request

from core.config import settings as s
from core.log import logger


def logging_dependency(request: Request) -> None:
    """Логируем обращение к эндпоинту."""
    logger.info(s.MESSAGE_INFO_ENDPOINT_CALL.format(method=request.method, url=request.url))
