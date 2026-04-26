from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_async_session
from workplaces.schemas import WorkplaceReadSchema
from workplaces.service import workplaces_service

api_workplaces_router = APIRouter()


@api_workplaces_router.get(
    '/', response_model=list[WorkplaceReadSchema],
    summary='Получить все рабочие места'
)
async def get_workplaces(
    session: AsyncSession = Depends(get_async_session)
) -> list[WorkplaceReadSchema]:
    """Эндпоинт получения всех рабочих мест."""
    workplaces = await workplaces_service.get_all(session)
    return workplaces


@api_workplaces_router.get(
    '/{workplace_id}',
    response_model=WorkplaceReadSchema,
    summary='Получить рабочее место'
)
async def get_workplace(
    workplace_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> WorkplaceReadSchema:
    """Эндпоинт получения рабочего места."""
    workplace = await workplaces_service.get(session, workplace_id)
    return workplace
