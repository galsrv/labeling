from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import is_sgtins_view_permitted
from core.config import settings as s
from core.dependencies import logging_dependency
from database.config import get_async_session
from frontend.responses import JsonToFrontendResponse
from sgtins.service import sgtin_service

api_sgtin_router = APIRouter()


@api_sgtin_router.post(
        '/sgtin_batch_insert',
        response_model=JsonToFrontendResponse,
        name='web_sgtin_batch_insert',
        summary='Пакетный импорт кодов',
        dependencies=[Depends(is_sgtins_view_permitted), Depends(logging_dependency)],
)
async def web_sgtin_batch_insert(
    file: UploadFile = File(),
    session: AsyncSession = Depends(get_async_session),
) -> JsonToFrontendResponse:
    """Загружаем коды маркировки в БД."""
    if not file.size or file.size > s.SGTIN_INSERT_MAX_FILE_SIZE_BYTES:
        return JsonToFrontendResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    file_bytes: bytes = await file.read()

    return await sgtin_service.batch_insert(file_bytes, session)
