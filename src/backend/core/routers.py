from fastapi import APIRouter

from core.config import settings as s
from drivers.api_views import drivers_router
from items.api_views import items_router
from frontend.views import web_root_router
from printers.api_views import printers_router
from transactions.api_views import api_orders_router
from workplaces.api_views import scales_router, workplace_router

from items.web_views import web_items_router
from labels.web_views import web_labels_router
from printers.web_views import web_printers_router
from scales.web_views import web_scales_router
from transactions.web_views import web_orders_router
from workplaces.web_views import web_workplaces_router

api_router = APIRouter(prefix=s.API_URL_PREFIX)

api_router.include_router(items_router, prefix='/items', tags=['items'])
api_router.include_router(api_orders_router, prefix='/orders', tags=['orders'])
api_router.include_router(drivers_router, prefix='/drivers', tags=['workplaces'])
api_router.include_router(scales_router, prefix='/scales', tags=['workplaces'])
api_router.include_router(printers_router, prefix='/printers', tags=['workplaces'])
api_router.include_router(workplace_router, prefix='/workplaces', tags=['workplaces'])

web_router = APIRouter(prefix=s.WEB_URL_PREFIX)

web_router.include_router(web_root_router, tags=['html endpoints'])
web_router.include_router(web_items_router, prefix='/items', tags=['html endpoints'])
web_router.include_router(web_labels_router, prefix='/labels', tags=['html endpoints'])
web_router.include_router(web_orders_router, prefix='/orders', tags=['html endpoints'])
web_router.include_router(web_scales_router, prefix='/scales', tags=['html endpoints'])
web_router.include_router(web_printers_router, prefix='/printers', tags=['html endpoints'])
web_router.include_router(web_workplaces_router, prefix='/workplaces', tags=['html endpoints'])
