from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from workplaces.repository import workplaces_repo
from workplaces.schemas import (
    WorkplaceReadWebSchema,
)

T = TypeVar('T', bound=BaseModel)


class WorkplacesService:
    """Сервисный слой для рабочих мест."""

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все рабочие места."""
        workplaces = await workplaces_repo.get_all(session)
        workplaces_dto = [WorkplaceReadWebSchema.model_validate(workplace) for workplace in workplaces]
        return workplaces_dto

    async def get(self, session: AsyncSession, workplace_id: int) -> T:
        """Возвращаем из БД рабочее место по его id."""
        workplace = await workplaces_repo.get(session, workplace_id)

        if workplace is None:
            raise ObjectNotFound(s.MESSAGE_ENTRY_DOESNT_EXIST)

        workplace_dto = WorkplaceReadWebSchema.model_validate(workplace)
        return workplace_dto


workplaces_service = WorkplacesService()
