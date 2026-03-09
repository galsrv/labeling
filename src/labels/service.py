from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_drivers.drivers import get_printer_driver, printer_drivers
from device_drivers.printers.printers_base import BasePrinterDriver
from device_drivers.validators import DeviceResponse

from items.service import web_items_service
from items.schemas import ItemWebSchema
from frontend.responses import WebJsonResponse
from labels.repository import label_repo
from labels.schemas import (
    PrintLabelTestPayload,
    LabelTemplatesReadWebSchema,
    LabelTemplatesCreateUpdateWebSchema
)
from labels.variables import get_control_codes, get_label_variables
from labels.utils import build_print_command
from printers.schemas import PrinterReadWebSchema
from printers.service import printers_service

T = TypeVar('T', bound=BaseModel)


class LabelTemplatesService:
    """Сервисный слой для шаблонов этикеток."""

    async def __get_common_context(self, session: AsyncSession) -> dict:
        """Получаем общие элементы контекста."""
        items = await web_items_service.get_all(session)
        printers = await printers_service.get_all(session)
        control_codes = get_control_codes()
        label_variables = get_label_variables()

        return {
            'drivers': printer_drivers.keys(),
            'control_codes': control_codes,
            'label_variables': label_variables,
            'items': items,
            'printers': printers
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все шаблоны этикеток."""
        labels = await label_repo.get_all(session)
        labels_dto = [LabelTemplatesReadWebSchema.model_validate(label) for label in labels]
        return labels_dto

    async def get(self, session: AsyncSession, label_id: int) -> T:
        """Возвращаем из БД шаблон этикетки по его id."""
        label = await label_repo.get(session, label_id)

        if label is None:
            raise ObjectNotFound(s.MESSAGE_ENTRY_DOESNT_EXIST)

        label_dto = LabelTemplatesReadWebSchema.model_validate(label)

        return label_dto

    async def update_form(self, session: AsyncSession, label_id: int) -> dict:
        """Формируем контекст формы изменения шаблона этикетки по его id."""
        label_dto = await self.get(session, label_id)
        context: dict = await self.__get_common_context(session)

        context.update({
            'mode': 'update',
            'label': label_dto,
        })

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Создаем шаблон этикетки."""
        context: dict = await self.__get_common_context(session)

        context.update({
            'mode': 'create',
            'label': None,
        })

        return context

    async def create(self, session: AsyncSession, name: str, driver_name: str, print_command: str) -> int:
        """Создаем шаблон этикетки, возвращаем его id."""
        label_template_dto = LabelTemplatesCreateUpdateWebSchema(
            name=name,
            driver_name=driver_name,
            print_command=print_command)

        label_id = await label_repo.create(session, label_template_dto)

        return label_id

    async def update(self, session: AsyncSession, label_id: int, name: str, driver_name: str, print_command: str) -> None:
        """Изменяем шаблон этикетки, ничего не возвращаем."""
        label_template_dto = LabelTemplatesCreateUpdateWebSchema(
            name=name,
            driver_name=driver_name,
            print_command=print_command)

        await label_repo.update(session, label_id, label_template_dto)

    async def delete(self, session: AsyncSession, label_id: int) -> None:
        """Удаляем шаблон этикетки, ничего не возвращаем."""
        await label_repo.delete(session, label_id)

    async def print_test_label(self, session: AsyncSession, label: PrintLabelTestPayload) -> WebJsonResponse:
        """Печатаем тестовую этикетку."""
        item_dto: ItemWebSchema = await web_items_service.get(session, label.item_id)
        printer_dto: PrinterReadWebSchema = await printers_service.get(session, label.printer_id)

        command_to_print = build_print_command(label.print_command, {'items': item_dto})
        driver: BasePrinterDriver | None = get_printer_driver(printer_dto.driver_name)

        if not driver:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await driver.print_label(printer_dto.ip.compressed, printer_dto.port, command_to_print)

        return WebJsonResponse(ok=response.ok, message=response.message)


labels_service = LabelTemplatesService()
