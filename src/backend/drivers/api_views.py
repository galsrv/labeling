from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session

from drivers.service import api_drivers_service
from scales.schemas import DeviceDriversReadSchema

drivers_router = APIRouter()


@drivers_router.get(
    '/', response_model=list[DeviceDriversReadSchema], summary='Получить все драйверы')
async def get_all_drivers(
    session: AsyncSession = Depends(get_async_session)
) -> list[DeviceDriversReadSchema]:
    """Эндпоинт получения всех драйверов."""
    scales = await api_drivers_service.get_all(session)
    return scales
