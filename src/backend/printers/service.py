from typing import TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_controller.controllers import get_printer_controller
from device_controller.printers.printers_base import BasePrinterController
from device_controller.validators import DeviceResponse

from drivers.models import DriverType
from drivers.service import web_drivers_service

from frontend.responses import WebJsonResponse

from printers.schemas import (
    PrinterShortSchema,
    PrintersReadSchema,
    PrintersWebSchema,
    PrintersCreateUpdateSchema,
    PrintersCreateUpdateWebSchema,
    PrinterFontSchema,
    PrinterImageSchema
)
from printers.repository import printers_repo


T = TypeVar('T', bound=BaseModel)


class PrintersService:
    """Сервисный слой для принтеров."""
    def __init__(self, read_model: type[BaseModel], create_update_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model
        self.create_update_model = create_update_model

    async def __get_common_context(self, session: AsyncSession) -> dict:
        """Получаем общие элементы контекста."""
        printer_drivers = await web_drivers_service.get_by_type(session, driver_type=DriverType.PRINTER)

        return {
            'drivers': printer_drivers,
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все принтеры."""
        printers = await printers_repo.get_all(session)
        printers_dto = [self.read_model.model_validate(printer) for printer in printers]
        return printers_dto

    async def get(self, session: AsyncSession, printer_id: int) -> T:
        """Возвращаем принтер по его id."""
        printer = await printers_repo.get(session, printer_id)

        if printer is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        printer_dto = self.read_model.model_validate(printer)

        return printer_dto

    async def update_form(self, session: AsyncSession, printer_id: int) -> dict:
        """Формируем контекст формы изменения принтера."""
        context: dict = await self.__get_common_context(session)

        printer_dto: PrintersWebSchema = await self.get(session, printer_id)
        controller: BasePrinterController | None = get_printer_controller(printer_dto.driver.name)

        context['default_command'] = controller._get_default_command() if controller else ''

        context.update({
            'mode': 'update',
            'printer': printer_dto,
        })

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Формируем контекст формы создания принтера."""
        context: dict = await self.__get_common_context(session)

        context.update({
            'mode': 'create',
            'printer': None,
        })

        return context

    async def create(self, session: AsyncSession, ip: str, port: int, driver_id: int, description: str) -> int | None:
        """Создаем принтер, возвращаем его id."""
        try:
            printer_dto = self.create_update_model(
                ip=ip,
                port=port,
                driver_id=driver_id,
                description=description)
        except ValidationError:
            return None

        printer_id: int | None = await printers_repo.create(session, printer_dto)

        return printer_id

    async def update(self, session: AsyncSession, printer_id: int, ip: str, port: int, driver_id: int, description: str) -> None:
        """Изменяем данные принтера, ничего не возвращаем."""
        try:
            printer_dto = self.create_update_model(
                ip=ip,
                port=port,
                driver_id=driver_id,
                description=description)
        except ValidationError:
            return None

        printer_id: int | None = await printers_repo.update(session, printer_id, printer_dto)

        return printer_id

    async def delete(self, session: AsyncSession, printer_id: int) -> None:
        """Удаляем принтер, ничего не возвращаем."""
        await printers_repo.delete(session, printer_id)

    async def test_connection(self, printer: PrinterShortSchema) -> WebJsonResponse:
        """Проверяем доступность принтера."""
        controller: BasePrinterController | None = get_printer_controller(printer.driver_name)

        if controller is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await controller.test_connection(printer.ip.compressed, printer.port)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def load_font(self, printer: PrinterShortSchema, font: PrinterFontSchema) -> WebJsonResponse:
        """Загружаем шрифт в принтер."""
        controller: BasePrinterController | None = get_printer_controller(printer.driver_name)

        if controller is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await controller.load_font(printer.ip.compressed, printer.port, font.file_bytes, font.filename, font.font_id)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def load_image(self, printer: PrinterShortSchema, image: PrinterImageSchema) -> WebJsonResponse:
        """Загружаем картинку в принтер."""
        controller: BasePrinterController | None = get_printer_controller(printer.driver_name)

        if controller is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await controller.load_image(printer.ip.compressed, printer.port, image.file_bytes, image.filename)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def send_arbitrary_command(self, printer: PrinterShortSchema, command: str) -> WebJsonResponse:
        """Отправляем на принтер произвольную команду."""
        controller: BasePrinterController | None = get_printer_controller(printer.driver_name)

        if controller is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await controller.send_arbitrary_command(printer.ip.compressed, printer.port, command)

        return WebJsonResponse(ok=response.ok, data=response.data, message=response.message)


api_printers_service = PrintersService(
    read_model=PrintersReadSchema,
    create_update_model=PrintersCreateUpdateSchema
)
web_printers_service = PrintersService(
    read_model=PrintersWebSchema,
    create_update_model=PrintersCreateUpdateWebSchema
)
