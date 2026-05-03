from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from drivers.drivers import get_printer_driver
from drivers.printers.printers_base import BasePrinterDriver
from drivers.validators import DeviceResponse
from frontend.responses import JsonToFrontendResponse
from items.schemas import ItemReadSchema
from items.service import items_service
from labels.repository import label_repo
from labels.schemas import LabelTemplatesCreateUpdateSchema, LabelTemplatesPageSchema, LabelTemplatesReadSchema, PrintLabelTestPayload
from labels.utils import build_print_command
from printers.schemas import PrinterReadSchema
from printers.service import printers_service

T = TypeVar('T', bound=BaseModel)


class LabelTemplatesService:
    """Сервисный слой для шаблонов этикеток."""

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> LabelTemplatesPageSchema:
        """Возвращаем из БД страницу списка шаблонов этикеток."""
        items, page, pages, size, total = await label_repo.get_page(session, page, size)

        labels_page_dto = LabelTemplatesPageSchema(
            items=[LabelTemplatesReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return labels_page_dto

    async def get(self, session: AsyncSession, label_id: int) -> T:
        """Возвращаем из БД шаблон этикетки по его id."""
        label_orm = await label_repo.get(session, label_id)
        label_dto = LabelTemplatesReadSchema.model_validate(label_orm)
        return label_dto

    async def create(self, session: AsyncSession, label_dto: LabelTemplatesCreateUpdateSchema) -> LabelTemplatesReadSchema:
        """Создаем шаблон этикетки, возвращаем его."""
        label_orm = await label_repo.create(session, label_dto)
        return LabelTemplatesReadSchema.model_validate(label_orm)

    async def update(self, session: AsyncSession, label_id: int, label_dto: LabelTemplatesCreateUpdateSchema) -> LabelTemplatesReadSchema:
        """Изменяем шаблон этикетки, возвращаем его."""
        label_orm = await label_repo.update(session, label_id, label_dto)
        return LabelTemplatesReadSchema.model_validate(label_orm)

    async def delete(self, session: AsyncSession, label_id: int) -> None:
        """Удаляем шаблон этикетки, ничего не возвращаем."""
        await label_repo.delete(session, label_id)

    async def print_test_label(self, session: AsyncSession, label: PrintLabelTestPayload) -> JsonToFrontendResponse:
        """Печатаем тестовую этикетку."""
        item_dto: ItemReadSchema = await items_service.get(session, label.item_id)
        printer_dto: PrinterReadSchema = await printers_service.get(session, label.printer_id)

        command_to_print = build_print_command(label.print_command, {'items': item_dto})
        driver: BasePrinterDriver | None = get_printer_driver(printer_dto.driver_name)

        if not driver:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.print_label(printer_dto.ip.compressed, printer_dto.port, command_to_print)

        return JsonToFrontendResponse(ok=response.ok, message=response.message)

    async def print_label(self, session: AsyncSession, printer_dto: PrinterReadSchema, label_command: str, label_context: dict) -> JsonToFrontendResponse:
        """Печатаем этикетку."""
        command_to_print = build_print_command(label_command, label_context)
        driver: BasePrinterDriver | None = get_printer_driver(printer_dto.driver_name)

        if not driver:
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.print_label(printer_dto.ip.compressed, printer_dto.port, command_to_print)

        return JsonToFrontendResponse(ok=response.ok, message=response.message)


labels_service = LabelTemplatesService()
