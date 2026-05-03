from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from frontend.responses import JsonToFrontendResponse
from sgtins.models import SgtinStatus
from sgtins.repository import sgtin_repo
from sgtins.schema import SgtinCreateSchema, SgtinSchema, SgtinUpdateSchema
from sgtins.utils import gtins_in_file_validation, load_marking_codes_from_file


class SgtinService:
    """Сервисный слой для кодов маркировки."""

    async def get_all(self, session: AsyncSession) -> list[SgtinSchema]:
        """Возвращаем все коды маркировки."""
        sgtins = await sgtin_repo.get_all(session)
        sgtins_dto_list = [SgtinSchema.model_validate(sgtin) for sgtin in sgtins]
        return sgtins_dto_list

    async def get_all_by_gtin(self, session: AsyncSession, gtin: int) -> list[SgtinSchema]:
        """Возвращаем все доступные для печати коды маркировки по GTIN."""
        sgtins = await sgtin_repo.get_all_by_gtin(session, gtin)
        sgtins_dto_list = [SgtinSchema.model_validate(sgtin) for sgtin in sgtins]
        return sgtins_dto_list

    async def batch_status_change(self, session: AsyncSession, ids: list[int], status_to_set: SgtinStatus = SgtinStatus.PRINTED) -> bool:
        """Массово меняем статус кодов маркировки."""
        if not ids:
            return False

        sgtin_update_dto = SgtinUpdateSchema(status=SgtinStatus.PRINTED, printed_at=datetime.now())

        return await sgtin_repo.batch_update(session, ids, sgtin_update_dto)

    async def batch_insert(self, file: bytes, session: AsyncSession) -> JsonToFrontendResponse:
        """Записываем в БД коды из файла.

        1. Проверяем корректность структуры файла.
        2. Проверяем наличие в БД всех GTIN из файла.
        3. Массово создаем коды маркировки в БД.
        """
        try:
            input_data: list[tuple[str, str, str]] = load_marking_codes_from_file(file)
        except Exception as e:
            logger.warning(str(e))
            return JsonToFrontendResponse(ok=False, message=str(e))

        try:
            await gtins_in_file_validation(input_data, session)
        except ValueError as e:
            logger.warning(str(e))
            return JsonToFrontendResponse(ok=False, message=str(e))

        sgtin_dtos = [SgtinCreateSchema(gtin=el[0], sgtin=el[1], crypto_end=el[2]) for el in input_data]

        if await sgtin_repo.batch_create(session, sgtin_dtos):
            logger.warning(s.MESSAGE_SUCCESSFUL_FILE_PROCESSING)
            return JsonToFrontendResponse(ok=True, message=s.MESSAGE_SUCCESSFUL_FILE_PROCESSING)

        logger.warning(s.MESSAGE_ERROR_LOADING_SGTIN_FILE)
        return JsonToFrontendResponse(ok=False, message=s.MESSAGE_ERROR_LOADING_SGTIN_FILE)


sgtin_service = SgtinService()
