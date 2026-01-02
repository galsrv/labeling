from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from workplaces.repository import drivers_repo, scales_repo, printers_repo, workplaces_repo
from workplaces.schemas import (
    DeviceDriversReadSchema,
    DeviceDriversWebSchema,
    ScalesReadSchema,
    ScalesWebSchema,
    PrintersReadSchema,
    PrintersWebSchema,
    WorkplaceReadSchema,
    WorkplaceWebSchema
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

    async def get(self, session: AsyncSession, driver_id: int) -> T:
        """Возвращаем из БД драйвер по его id."""
        driver = await drivers_repo.get(session, driver_id)

        if driver is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        driver_dto = self.read_model.model_validate(driver)
        return driver_dto


class ScalesService:
    """Сервисный слой для весов."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

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


class PintersService:
    """Сервисный слой для принтеров."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все принтеры."""
        printers = await printers_repo.get_all(session)
        printers_dto = [self.read_model.model_validate(printer) for printer in printers]
        return printers_dto

    async def get(self, session: AsyncSession, printer_id: int) -> T:
        """Возвращаем из БД принтер по его id."""
        printer = await printers_repo.get(session, printer_id)

        if printer is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        printer_dto = self.read_model.model_validate(printer)
        return printer_dto


class WorkplacesService:
    """Сервисный слой для рабочих мест."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все рабочие места."""
        workplaces = await workplaces_repo.get_all(session)
        workplaces_dto = [self.read_model.model_validate(workplace) for workplace in workplaces]
        return workplaces_dto

    async def get(self, session: AsyncSession, workplace_id: int) -> T:
        """Возвращаем из БД рабочее место по его id."""
        workplace = await workplaces_repo.get(session, workplace_id)

        if workplace is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        workplace_dto = self.read_model.model_validate(workplace)
        return workplace_dto


api_drivers_service = DriversService(read_model=DeviceDriversReadSchema)
web_drivers_service = DriversService(read_model=DeviceDriversWebSchema)

api_scales_service = ScalesService(read_model=ScalesReadSchema)
web_scales_service = ScalesService(read_model=ScalesWebSchema)

api_printers_service = PintersService(read_model=PrintersReadSchema)
web_printers_service = PintersService(read_model=PrintersWebSchema)

api_workplaces_service = WorkplacesService(read_model=WorkplaceReadSchema)
web_workplaces_service = WorkplacesService(read_model=WorkplaceWebSchema)
