from fastapi import APIRouter

from core.config import settings as s
from items.api_views import items_router
from transactions.api_views import api_orders_router
from workplaces.views import drivers_router, scales_router, printers_router, workplace_router

from transactions.web_views import web_orders_router

api_router = APIRouter(prefix=s.API_URL_PREFIX)

api_router.include_router(items_router, prefix='/items', tags=['items'])
api_router.include_router(api_orders_router, prefix='/orders', tags=['orders'])
api_router.include_router(drivers_router, prefix='/drivers', tags=['workplaces'])
api_router.include_router(scales_router, prefix='/scales', tags=['workplaces'])
api_router.include_router(printers_router, prefix='/printers', tags=['workplaces'])
api_router.include_router(workplace_router, prefix='/workplaces', tags=['workplaces'])

web_router = APIRouter(prefix=s.WEB_URL_PREFIX)

web_router.include_router(web_orders_router, prefix='/orders', tags=['html endpoints'])
