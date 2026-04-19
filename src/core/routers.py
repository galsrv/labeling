from fastapi import APIRouter

from core.config import settings as s

from frontend.views import html_root_router

from items.api_views import api_items_router
from labels.api_views import api_labels_router
from drivers.api_views import api_drivers_router
from orders.api_views import api_orders_router
from sgtins.api_views import api_sgtin_router
from scales.api_views import api_scales_router
from printers.api_views import api_printers_router
from workplaces.api_views import api_workplaces_router

from items.html_views import html_items_router
from labels.html_views import html_labels_router
from printers.html_views import html_printers_router
from scales.html_views import html_scales_router
from sgtins.html_views import html_sgtin_router
from orders.html_views import html_orders_router
from workplaces.html_views import html_workplaces_router

from scales.websocket_views import webscoket_scales_router

api_router = APIRouter(prefix=s.API_URL_PREFIX)

api_router.include_router(api_items_router, prefix='/items', tags=['items'])
api_router.include_router(api_orders_router, prefix='/orders', tags=['orders'])
api_router.include_router(api_sgtin_router, prefix='/sgtins', tags=['sgtins'])
api_router.include_router(api_drivers_router, prefix='/drivers', tags=['drivers'])
api_router.include_router(api_labels_router, prefix='/labels', tags=['labels'])
api_router.include_router(api_scales_router, prefix='/scales', tags=['scales'])
api_router.include_router(api_printers_router, prefix='/printers', tags=['printers'])
api_router.include_router(api_workplaces_router, prefix='/workplaces', tags=['workplaces'])

html_router = APIRouter(prefix=s.HTML_URL_PREFIX)

html_router.include_router(html_root_router, tags=['html pages'])
html_router.include_router(html_items_router, prefix='/items', tags=['html pages'])
html_router.include_router(html_orders_router, prefix='/orders', tags=['html pages'])
html_router.include_router(html_scales_router, prefix='/scales', tags=['html pages'])
html_router.include_router(html_printers_router, prefix='/printers', tags=['html pages'])
html_router.include_router(html_workplaces_router, prefix='/workplaces', tags=['html pages'])
html_router.include_router(html_labels_router, prefix='/labels', tags=['html pages'])
html_router.include_router(html_sgtin_router, prefix='/sgtins', tags=['html pages'])

websocket_router = APIRouter(prefix=s.WEBSOCKET_URL_PREFIX)

websocket_router.include_router(webscoket_scales_router, prefix='/scales', tags=['websockets'])

root_router = APIRouter()

root_router.include_router(html_root_router, tags=['site root'])
