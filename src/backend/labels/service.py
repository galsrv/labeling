from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from labels.repository import label_repo
from labels.schemas import LabelTemplatesWebSchema, LabelTemplatesCreateUpdateWebSchema
from labels.variables import get_control_codes, get_label_variables
from workplaces.service import web_drivers_service, DriverType

T = TypeVar('T', bound=BaseModel)


class LabelTemplatesService:
    """Сервисный слой для шаблонов этикеток."""
    def __init__(self, read_model: type[BaseModel], create_update_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model
        self.create_update_model = create_update_model

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все шаблоны этикеток."""
        labels = await label_repo.get_all(session)
        labels_dto = [self.read_model.model_validate(label) for label in labels]
        return labels_dto

    async def get(self, session: AsyncSession, label_id: int) -> dict:
        """Возвращаем из БД шаблон этикетки по его id."""
        label = await label_repo.get(session, label_id)

        if label is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        label_dto = self.read_model.model_validate(label)
        printer_drivers = await web_drivers_service.get_by_type(session, driver_type=DriverType.PRINTER)
        control_codes = get_control_codes()
        label_variables = get_label_variables()

        context = {
            'mode': 'update',
            'label': label_dto,
            'drivers': printer_drivers,
            'control_codes': control_codes,
            'label_variables': label_variables,
        }

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Создаем шаблон этикетки."""
        printer_drivers = await web_drivers_service.get_by_type(session, driver_type=DriverType.PRINTER)
        control_codes = get_control_codes()
        label_variables = get_label_variables()

        context = {
            'mode': 'create',
            'label': None,
            'drivers': printer_drivers,
            'control_codes': control_codes,
            'label_variables': label_variables,
        }

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


web_labels_service = LabelTemplatesService(
    read_model=LabelTemplatesWebSchema,
    create_update_model=LabelTemplatesCreateUpdateWebSchema,
)
