from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s

from drivers.drivers import get_printer_driver
from drivers.printers.printers_base import BasePrinterDriver
from drivers.validators import DeviceResponse

from frontend.responses import JsonToFrontendResponse

from printers.schemas import (
    PrinterPageSchema,
    PrinterShortSchema,
    PrinterReadSchema,
    PrinterCreateUpdateSchema,
    PrinterFontSchema,
    PrinterImageSchema
)
from printers.repository import printers_repo


T = TypeVar('T', bound=BaseModel)


class PrintersService:
    """Сервисный слой для принтеров."""

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> PrinterPageSchema:
        """Возвращаем страницу списка принтеров."""
        items, page, pages, size, total = await printers_repo.get_page(session, page, size)

        printers_page_dto = PrinterPageSchema(
            items=[PrinterReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return printers_page_dto

    async def get(self, session: AsyncSession, printer_id: int) -> T:
        """Возвращаем принтер по его id."""
        printer = await printers_repo.get(session, printer_id)
        printer_dto = PrinterReadSchema.model_validate(printer)
        return printer_dto

    async def create(self, session: AsyncSession, printer_dto: PrinterCreateUpdateSchema) -> PrinterReadSchema:
        """Создаем принтер, возвращаем его."""
        printer_orm = await printers_repo.create(session, printer_dto)
        return PrinterReadSchema.model_validate(printer_orm)

    async def update(self, session: AsyncSession, printer_id: int, printer_dto: PrinterCreateUpdateSchema) -> PrinterReadSchema:
        """Изменяем принтер, возвращаем его."""
        printer_orm = await printers_repo.update(session, printer_id, printer_dto)
        return PrinterReadSchema.model_validate(printer_orm)

    async def delete(self, session: AsyncSession, printer_id: int) -> None:
        """Удаляем принтер, ничего не возвращаем."""
        await printers_repo.delete(session, printer_id)

    async def test_connection(self, printer: PrinterShortSchema) -> JsonToFrontendResponse:
        """Проверяем доступность принтера."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.test_connection(printer.ip.compressed, printer.port)

        return JsonToFrontendResponse(ok=response.ok, message=response.message)

    async def load_font(self, printer: PrinterShortSchema, font: PrinterFontSchema) -> JsonToFrontendResponse:
        """Загружаем шрифт в принтер."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.load_font(printer.ip.compressed, printer.port, font.file_bytes, font.filename, font.font_id)

        return JsonToFrontendResponse(ok=response.ok, message=response.message)

    async def load_image(self, printer: PrinterShortSchema, image: PrinterImageSchema) -> JsonToFrontendResponse:
        """Загружаем картинку в принтер."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.load_image(printer.ip.compressed, printer.port, image.file_bytes, image.filename)

        return JsonToFrontendResponse(ok=response.ok, message=response.message)

    async def send_arbitrary_command(self, printer: PrinterShortSchema, command: str) -> JsonToFrontendResponse:
        """Отправляем на принтер произвольную команду."""
        driver: BasePrinterDriver | None = get_printer_driver(printer.driver_name)

        if driver is None:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.send_arbitrary_command(printer.ip.compressed, printer.port, command)

        return JsonToFrontendResponse(ok=response.ok, data=response.data, message=response.message)


printers_service = PrintersService()
