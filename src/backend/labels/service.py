from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_controller.controllers import get_printer_controller
from device_controller.printers.printers_base import BasePrinterController
from device_controller.validators import DeviceResponse

from items.service import web_items_service
from items.schemas import ItemWebSchema
from frontend.responses import WebJsonResponse
from labels.repository import label_repo
from labels.schemas import (
    PrintLabelTestPayload,
    LabelTemplatesWebSchema,
    LabelTemplatesCreateUpdateWebSchema
)
from labels.variables import get_control_codes, get_label_variables
from labels.utils import build_print_command
from printers.schemas import PrintersWebSchema
from printers.service import web_printers_service, web_drivers_service, DriverType

T = TypeVar('T', bound=BaseModel)


class LabelTemplatesService:
    """Сервисный слой для шаблонов этикеток."""
    def __init__(self, read_model: type[BaseModel], create_update_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model
        self.create_update_model = create_update_model

    async def __get_common_context(self, session: AsyncSession) -> dict:
        """Получаем общие элементы контекста."""
        printer_drivers = await web_drivers_service.get_by_type(session, driver_type=DriverType.PRINTER)
        items = await web_items_service.get_all(session)
        printers = await web_printers_service.get_all(session)
        control_codes = get_control_codes()
        label_variables = get_label_variables()

        return {
            'drivers': printer_drivers,
            'control_codes': control_codes,
            'label_variables': label_variables,
            'items': items,
            'printers': printers
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все шаблоны этикеток."""
        labels = await label_repo.get_all(session)
        labels_dto = [self.read_model.model_validate(label) for label in labels]
        return labels_dto

    async def get(self, session: AsyncSession, label_id: int) -> T:
        """Возвращаем из БД шаблон этикетки по его id."""
        label = await label_repo.get(session, label_id)

        if label is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        label_dto = self.read_model.model_validate(label)

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

    async def create(self, session: AsyncSession, name: str, driver_id: int, print_command: str) -> int:
        """Создаем шаблон этикетки, возвращаем его id."""
        label_template_dto = self.create_update_model(
            name=name,
            driver_id=driver_id,
            print_command=print_command)

        label_id = await label_repo.create(session, label_template_dto)

        return label_id

    async def update(self, session: AsyncSession, label_id: int, name: str, driver_id: int, print_command: str) -> None:
        """Изменяем шаблон этикетки, ничего не возвращаем."""
        label_template_dto = self.create_update_model(
            name=name,
            driver_id=driver_id,
            print_command=print_command)

        await label_repo.update(session, label_id, label_template_dto)

    async def delete(self, session: AsyncSession, label_id: int) -> None:
        """Удаляем шаблон этикетки, ничего не возвращаем."""
        await label_repo.delete(session, label_id)

    async def print_test_label(self, session: AsyncSession, label: PrintLabelTestPayload) -> WebJsonResponse:
        """Печатаем тестовую этикетку."""
        item_dto: ItemWebSchema = await web_items_service.get(session, label.item_id)
        printer_dto: PrintersWebSchema = await web_printers_service.get(session, label.printer_id)

        command_to_print = build_print_command(label.print_command, {'items': item_dto})
        controller: BasePrinterController | None = get_printer_controller(printer_dto.driver.name)

        if not controller:
            return WebJsonResponse(ok=False, message=s.MESSAGE_DRIVER_NOT_FOUND)

        response: DeviceResponse = await controller.print_label(printer_dto.ip.compressed, printer_dto.port, command_to_print)

        return WebJsonResponse(ok=response.ok, message=response.message)


web_labels_service = LabelTemplatesService(
    read_model=LabelTemplatesWebSchema,
    create_update_model=LabelTemplatesCreateUpdateWebSchema,
)
