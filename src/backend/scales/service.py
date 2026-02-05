from typing import TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_controller.validators import ScalesResponse
from drivers.models import DriverType
from drivers.service import web_drivers_service

from frontend.responses import WebJsonResponse

from scales.repository import scales_repo
from scales.schemas import (
    ScalesReadSchema,
    ScalesShortSchema,
    ScalesWebSchema,
    ScalesCreateUpdateSchema,
    ScalesCreateUpdateWebSchema,
)

T = TypeVar('T', bound=BaseModel)


class ScalesService:
    """Сервисный слой для весов."""
    def __init__(self, read_model: type[BaseModel], create_update_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model
        self.create_update_model = create_update_model

    async def __get_common_context(self, session: AsyncSession) -> dict:
        """Получаем общие элементы контекста."""
        scales_drivers = await web_drivers_service.get_by_type(session, driver_type=DriverType.SCALES)

        return {
            'drivers': scales_drivers,
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все весы."""
        scales = await scales_repo.get_all(session)
        scales_dto = [self.read_model.model_validate(scales) for scales in scales]
        return scales_dto

    async def get(self, session: AsyncSession, scales_id: int) -> T:
        """Возвращаем из БД весы по их id."""
        scales = await scales_repo.get(session, scales_id)

        if scales is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        scales_dto = self.read_model.model_validate(scales)
        return scales_dto

    async def update_form(self, session: AsyncSession, scales_id: int) -> dict:
        """Формируем контекст формы изменения весов."""
        context: dict = await self.__get_common_context(session)
        scales_dto: ScalesWebSchema = await self.get(session, scales_id)

        context.update({
            'mode': 'update',
            'scales': scales_dto,
        })

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Формируем контекст формы создания весов."""
        context: dict = await self.__get_common_context(session)

        context.update({
            'mode': 'create',
            'scales': None,
        })

        return context

    async def create(self, session: AsyncSession, ip: str, port: int, driver_id: int, description: str) -> int | None:
        """Создаем весы, возвращаем их id."""
        try:
            scales_dto = self.create_update_model(
                ip=ip,
                port=port,
                driver_id=driver_id,
                description=description)
        except ValidationError as e:
            from core.log import logger
            logger.debug(str(e))
            return None

        scales_id: int | None = await scales_repo.create(session, scales_dto)

        return scales_id

    async def update(self, session: AsyncSession, scales_id: int, ip: str, port: int, driver_id: int, description: str) -> None:
        """Изменяем данные весов, ничего не возвращаем."""
        try:
            scales_dto = self.create_update_model(
                ip=ip,
                port=port,
                driver_id=driver_id,
                description=description)
        except ValidationError:
            return None

        scales_id: int | None = await scales_repo.update(session, scales_id, scales_dto)

        return scales_id

    async def delete(self, session: AsyncSession, scales_id: int) -> None:
        """Удаляем весы, ничего не возвращаем."""
        await scales_repo.delete(session, scales_id)

    async def get_weight(self, scales: ScalesShortSchema) -> None:
        """Получаем вес с весов."""
        # to be programmed
        response = ScalesResponse(weight=1.234, stable=True, overload=False)
        return WebJsonResponse(ok=True, data=response, message=s.MESSAGE_CONNECTION_SUCCESSFUL)


api_scales_service = ScalesService(
    read_model=ScalesReadSchema,
    create_update_model=ScalesCreateUpdateSchema,
)
web_scales_service = ScalesService(
    read_model=ScalesWebSchema,
    create_update_model=ScalesCreateUpdateWebSchema,
)
