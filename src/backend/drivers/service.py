from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from drivers.models import DriverType
from drivers.repository import drivers_repo
from workplaces.schemas import (
    DeviceDriversReadSchema,
    DeviceDriversWebSchema,
)

T = TypeVar('T', bound=BaseModel)


class DriversService:
    """Сервисный слой для драйверов."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все драйверы."""
        drivers = await drivers_repo.get_all(session)
        drivers_dto = [self.read_model.model_validate(driver) for driver in drivers]
        return drivers_dto

    async def get_by_type(self, session: AsyncSession, driver_type: DriverType) -> list[T]:
        """Получаем драйверы определенного типа."""
        drivers_by_type = await drivers_repo.get_by_type(session, driver_type)
        drivers_by_type_dto = [self.read_model.model_validate(driver) for driver in drivers_by_type]
        return drivers_by_type_dto

    async def get(self, session: AsyncSession, driver_id: int) -> T:
        """Возвращаем из БД драйвер по его id."""
        driver = await drivers_repo.get(session, driver_id)

        if driver is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        driver_dto = self.read_model.model_validate(driver)
        return driver_dto


api_drivers_service = DriversService(read_model=DeviceDriversReadSchema)
web_drivers_service = DriversService(read_model=DeviceDriversWebSchema)
