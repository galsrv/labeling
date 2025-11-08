from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.config import settings as s
from workplaces.models import ScalesOrm, WorkplaceOrm


class ScalesService(BaseService):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ScalesOrm)

    async def get_all_scales(
        self,
        session: AsyncSession,
    ) -> list[ScalesOrm]:
        """Получаем все весы."""
        scales = await self.get_all(session)
        return scales

    async def get_scales(
        self,
        session: AsyncSession,
        scales_id: int,
    ) -> ScalesOrm:
        """Получаем весы."""
        scales: ScalesOrm | None = await self.get(session, scales_id)

        if scales is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        return scales

class WorkplaceService(BaseService):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(WorkplaceOrm)

    async def get_all_workplaces(
        self,
        session: AsyncSession,
    ) -> list[WorkplaceOrm]:
        """Получаем все рабочие места."""
        workplaces = await self.get_all(session)
        return workplaces

    async def get_workplace(
        self,
        session: AsyncSession,
        workplace_id: int,
    ) -> WorkplaceOrm:
        """Получаем рабочее место."""
        workplace: WorkplaceOrm | None = await self.get(session, workplace_id)

        if workplace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        return workplace


scales_service = ScalesService()

workplaces_service = WorkplaceService()
