from fastapi import APIRouter, Depends, File, Request, UploadFile

from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.database import get_async_session
from core.dependencies import logging_dependency
from core.config import templates
from frontend.responses import WebJsonResponse

from sgtins.service import sgtin_service

sgtin_router = APIRouter()


@sgtin_router.post(
        '/sgtin_batch_insert',
        response_model=WebJsonResponse,
        name='web_sgtin_batch_insert',
        summary='Пакетный импорт кодов',
        dependencies=[Depends(logging_dependency)]
)
async def web_sgtin_batch_insert(
    file: UploadFile = File(),
    session: AsyncSession = Depends(get_async_session),
) -> WebJsonResponse:
    """Загружаем коды маркировки в БД."""
    if not file.size or file.size > s.SGTIN_INSERT_MAX_FILE_SIZE_BYTES:
        return WebJsonResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    file_bytes: bytes = await file.read()

    return await sgtin_service.batch_insert(file_bytes, session)


@sgtin_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Базовый интерфейс кодов маркировки',
        name='read_sgtins',
        dependencies=[Depends(logging_dependency)]
)
async def web_read_sgtins(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Базовый интерфейс кодов маркировки."""
    return templates.TemplateResponse(
        request=request,
        name='sgtins.html'
    )
