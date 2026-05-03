from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from workplaces.repository import workplaces_repo
from workplaces.schemas import (
    WorkplacePageSchema,
    WorkplaceReadSchema,
)

T = TypeVar('T', bound=BaseModel)


class WorkplacesService:
    """Сервисный слой для рабочих мест."""

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> WorkplacePageSchema:
        """Возвращаем из страницу списка рабочих мест."""
        items, page, pages, size, total = await workplaces_repo.get_page(session, page, size)

        workplaces_page_dto = WorkplacePageSchema(
            items=[WorkplaceReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return workplaces_page_dto

    async def get(self, session: AsyncSession, workplace_id: int) -> T:
        """Возвращаем из БД рабочее место по его id."""
        workplace = await workplaces_repo.get(session, workplace_id)
        workplace_dto = WorkplaceReadSchema.model_validate(workplace)
        return workplace_dto


workplaces_service = WorkplacesService()
