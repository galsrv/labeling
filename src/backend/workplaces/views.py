from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from workplaces.schemas import ScalesReadSchema, WorkplaceReadSchema
from workplaces.service import scales_service, workplaces_service

scales_router = APIRouter()

workplace_router = APIRouter()

@scales_router.get(
    '/', response_model=list[ScalesReadSchema], summary='Получить все весы')
async def get_all_scales(
    session: AsyncSession = Depends(get_async_session)
) -> list[ScalesReadSchema]:
    """Эндпоинт получения всех весов."""
    scales = await scales_service.get_all_scales(session)
    return scales # pyright: ignore[reportReturnType]

@scales_router.get(
    '/{scales_id}', response_model=ScalesReadSchema, summary='Получить весы')
async def get_scales(
    scales_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт получения весов."""
    order = await scales_service.get_scales(session, scales_id)
    return order # pyright: ignore[reportReturnType]

@workplace_router.get(
    '/', response_model=list[WorkplaceReadSchema], summary='Получить все рабочие места')
async def get_all_workplaces(
    session: AsyncSession = Depends(get_async_session)
) -> list[WorkplaceReadSchema]:
    """Эндпоинт получения всех рабочих мест."""
    workplaces = await workplaces_service.get_all_workplaces(session)
    return workplaces # pyright: ignore[reportReturnType]

@workplace_router.get(
    '/{workplace_id}', response_model=WorkplaceReadSchema, summary='Получить рабочее место')
async def get_workplace(
    workplace_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> WorkplaceReadSchema:
    """Эндпоинт получения рабочего места."""
    workplace = await workplaces_service.get_workplace(session, workplace_id)
    return workplace # pyright: ignore[reportReturnType]