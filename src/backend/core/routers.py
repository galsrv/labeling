from fastapi import APIRouter

from core.config import settings as s
from items.views import items_router
from transactions.views import orders_router
from workplaces.views import drivers_router, scales_router, workplace_router

main_router = APIRouter(prefix=s.API_URL_PREFIX)

main_router.include_router(items_router, prefix='/items', tags=['items'])
main_router.include_router(orders_router, prefix='/orders', tags=['orders'])
main_router.include_router(drivers_router, prefix='/drivers', tags=['workplaces'])
main_router.include_router(scales_router, prefix='/scales', tags=['workplaces'])
main_router.include_router(workplace_router, prefix='/workplaces', tags=['workplaces'])
