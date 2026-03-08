from fastapi import APIRouter

from core.config import settings as s

from frontend.views import web_root_router

from items.api_views import api_items_router
from transactions.api_views import api_orders_router

from items.views import items_router
from labels.web_views import labels_router
from printers.views import printers_router
from scales.views import scales_router
from transactions.views import orders_router
from workplaces.views import workplaces_router

api_router = APIRouter(prefix=s.API_URL_PREFIX)

api_router.include_router(api_items_router, prefix='/items', tags=['items'])
api_router.include_router(api_orders_router, prefix='/orders', tags=['orders'])

web_router = APIRouter(prefix=s.WEB_URL_PREFIX)

web_router.include_router(web_root_router, tags=['html endpoints'])
web_router.include_router(items_router, prefix='/items', tags=['html endpoints'])
web_router.include_router(orders_router, prefix='/orders', tags=['html endpoints'])
web_router.include_router(scales_router, prefix='/scales', tags=['html endpoints'])
web_router.include_router(printers_router, prefix='/printers', tags=['html endpoints'])
web_router.include_router(workplaces_router, prefix='/workplaces', tags=['html endpoints'])
web_router.include_router(labels_router, prefix='/labels', tags=['html endpoints'])

root_router = APIRouter()

root_router.include_router(web_root_router, tags=['site root'])
