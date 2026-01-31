from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from printers.schemas import PrintersReadSchema
from printers.service import api_printers_service

printers_router = APIRouter()


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
