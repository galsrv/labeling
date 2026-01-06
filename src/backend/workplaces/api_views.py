from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from workplaces.schemas import DeviceDriversReadSchema, ScalesReadSchema, PrintersReadSchema, WorkplaceReadSchema
from workplaces.service import api_drivers_service, api_scales_service, api_printers_service, api_workplaces_service

drivers_router = APIRouter()

scales_router = APIRouter()

printers_router = APIRouter()

workplace_router = APIRouter()


@drivers_router.get(
    '/', response_model=list[DeviceDriversReadSchema], summary='Получить все драйверы')
async def get_all_drivers(
    session: AsyncSession = Depends(get_async_session)
) -> list[DeviceDriversReadSchema]:
    """Эндпоинт получения всех драйверов."""
    scales = await api_drivers_service.get_all(session)
    return scales


@scales_router.get(
    '/', response_model=list[ScalesReadSchema], summary='Получить все весы')
async def get_all_scales(
    session: AsyncSession = Depends(get_async_session)
) -> list[ScalesReadSchema]:
    """Эндпоинт получения всех весов."""
    scales = await api_scales_service.get_all(session)
    return scales


@scales_router.get(
    '/{scales_id}', response_model=ScalesReadSchema, summary='Получить весы')
async def get_scales(
    scales_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> ScalesReadSchema:
    """Эндпоинт получения весов."""
    scales = await api_scales_service.get(session, scales_id)
    return scales


@printers_router.get(
    '/', response_model=list[PrintersReadSchema], summary='Получить все принтеры')
async def get_all_printers(
    session: AsyncSession = Depends(get_async_session)
) -> list[PrintersReadSchema]:
    """Эндпоинт получения всех принтеров."""
    printers = await api_printers_service.get_all(session)
    return printers


@printers_router.get(
    '/{printer_id}', response_model=PrintersReadSchema, summary='Получить принтер')
async def get_printer(
    printer_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> PrintersReadSchema:
    """Эндпоинт получения весов."""
    printer = await api_printers_service.get(session, printer_id)
    return printer


@workplace_router.get(
    '/', response_model=list[WorkplaceReadSchema], summary='Получить все рабочие места')
async def get_all_workplaces(
    session: AsyncSession = Depends(get_async_session)
) -> list[WorkplaceReadSchema]:
    """Эндпоинт получения всех рабочих мест."""
    workplaces = await api_workplaces_service.get_all(session)
    return workplaces


@workplace_router.get(
    '/{workplace_id}', response_model=WorkplaceReadSchema, summary='Получить рабочее место')
async def get_workplace(
    workplace_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> WorkplaceReadSchema:
    """Эндпоинт получения рабочего места."""
    workplace = await api_workplaces_service.get(session, workplace_id)
    return workplace
