from fastapi import APIRouter, Depends

from auth.dependencies import is_scales_view_permitted, is_printers_view_permitted
from core.dependencies import logging_dependency
from drivers.drivers import scales_drivers, printer_drivers

api_drivers_router = APIRouter()


@api_drivers_router.get(
    '/scales',
    response_model=list[str],
    summary='Получить все драйверы весов',
    dependencies=[Depends(is_scales_view_permitted), Depends(logging_dependency)]
)
async def get_all_scales_drivers(
) -> list[str]:
    """Эндпоинт получения всех имен драйверов."""
    drivers_names = list(scales_drivers.keys())
    return drivers_names


@api_drivers_router.get(
    '/printers',
    response_model=list[str],
    summary='Получить все драйверы принтеров',
    dependencies=[Depends(is_printers_view_permitted), Depends(logging_dependency)]
)
async def get_all_printers_drivers(
) -> list[str]:
    """Эндпоинт получения всех имен драйверов."""
    drivers_names = list(printer_drivers.keys())
    return drivers_names
