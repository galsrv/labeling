from typing import TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_drivers.drivers import printer_drivers, get_printer_driver
from device_drivers.printers.printers_base import BasePrinterDriver
from device_drivers.validators import DeviceResponse

from frontend.responses import WebJsonResponse

from printers.schemas import (
    PrinterShortSchema,
    PrinterReadWebSchema,
    PrinterCreateUpdateWebSchema,
    PrinterFontSchema,
    PrinterImageSchema
)
from printers.repository import printers_repo


T = TypeVar('T', bound=BaseModel)


class PrintersService:
    """Сервисный слой для принтеров."""
    # def __init__(self, read_model: type[BaseModel], create_update_model: type[BaseModel]) -> None:
    #     """Инициализация объекта класса."""
    #     self.read_model = read_model
    #     self.create_update_model = create_update_model

    async def __get_common_context(self) -> dict:
        """Получаем общие элементы контекста."""
        return {
            'drivers': printer_drivers.keys(),
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все принтеры."""
        printers = await printers_repo.get_all(session)
        printers_dto = [PrinterReadWebSchema.model_validate(printer) for printer in printers]
        return printers_dto

    async def get(self, session: AsyncSession, printer_id: int) -> T:
        """Возвращаем принтер по его id."""
        printer = await printers_repo.get(session, printer_id)

        if printer is None:
            raise ObjectNotFound(s.MESSAGE_ENTRY_DOESNT_EXIST)

        printer_dto = PrinterReadWebSchema.model_validate(printer)

        return printer_dto

    async def update_form(self, session: AsyncSession, printer_id: int) -> dict:
        """Формируем контекст формы изменения принтера."""
        context: dict = await self.__get_common_context()

        printer_dto: PrinterReadWebSchema = await self.get(session, printer_id)
        driver: BasePrinterDriver | None = get_printer_driver(printer_dto.driver_name)

        context['default_command'] = driver._get_default_command() if driver else ''

        context.update({
            'mode': 'update',
            'printer': printer_dto,
        })

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Формируем контекст формы создания принтера."""
        context: dict = await self.__get_common_context()

        context.update({
            'mode': 'create',
            'printer': None,
        })

        return context

    async def create(self, session: AsyncSession, ip: str, port: int, driver_name: str, description: str) -> int | None:
        """Создаем принтер, возвращаем его id."""
        try:
            printer_dto = PrinterCreateUpdateWebSchema(
                ip=ip,
                port=port,
                driver_name=driver_name,
                description=description)
        except ValidationError:
            return None

        printer_id: int | None = await printers_repo.create(session, printer_dto)

        return printer_id

    async def update(self, session: AsyncSession, printer_id: int, ip: str, port: int, driver_name: str, description: str) -> None:
        """Изменяем данные принтера, ничего не возвращаем."""
        try:
            printer_dto = PrinterCreateUpdateWebSchema(
                ip=ip,
                port=port,
                driver_name=driver_name,
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
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.test_connection(printer.ip.compressed, printer.port)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def load_font(self, printer: PrinterShortSchema, font: PrinterFontSchema) -> WebJsonResponse:
        """Загружаем шрифт в принтер."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.load_font(printer.ip.compressed, printer.port, font.file_bytes, font.filename, font.font_id)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def load_image(self, printer: PrinterShortSchema, image: PrinterImageSchema) -> WebJsonResponse:
        """Загружаем картинку в принтер."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.load_image(printer.ip.compressed, printer.port, image.file_bytes, image.filename)

        return WebJsonResponse(ok=response.ok, message=response.message)

    async def send_arbitrary_command(self, printer: PrinterShortSchema, command: str) -> WebJsonResponse:
        """Отправляем на принтер произвольную команду."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.send_arbitrary_command(printer.ip.compressed, printer.port, command)

        return WebJsonResponse(ok=response.ok, data=response.data, message=response.message)


printers_service = PrintersService()
