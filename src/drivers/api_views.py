from fastapi import APIRouter

from drivers.drivers import scales_drivers, printer_drivers

api_drivers_router = APIRouter()


@api_drivers_router.get(
    '/scales',
    response_model=list[str],
    summary='Получить все драйверы весов'
)
async def get_all_scales_drivers(
) -> list[str]:
    """Эндпоинт получения всех имен драйверов."""
    drivers_names = list(scales_drivers.keys())
    return drivers_names


@api_drivers_router.get(
    '/printers',
    response_model=list[str],
    summary='Получить все драйверы принтеров'
)
async def get_all_printers_drivers(
) -> list[str]:
    """Эндпоинт получения всех имен драйверов."""
    drivers_names = list(printer_drivers.keys())
    return drivers_names
