import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.config import settings as s
from core.exceptions import register_exception_handlers
from core.log import logger
from core.routers import api_router, root_router, html_router, websocket_router
from core.tasks import lifespan_tasks

fastapi_app = FastAPI(
    title=s.APP_TITLE,
    openapi_url=s.OPENAPI_URL,
    docs_url=s.DOCS_URL,
    redoc_url=s.REDOC_URL,
    lifespan=lifespan_tasks,
)

fastapi_app.include_router(api_router)
fastapi_app.include_router(html_router)
fastapi_app.include_router(root_router)
fastapi_app.include_router(websocket_router)

register_exception_handlers(fastapi_app)

fastapi_app.mount(s.STATIC_FILES_URL, StaticFiles(directory=s.STATIC_FILES_DIR))


if __name__ == '__main__':
    logger.info(s.MESSAGE_APP_STARTED.format(host=s.BACKEND_HOST, port=s.BACKEND_PORT))

    uvicorn.run(
        'main:fastapi_app',
        host=s.BACKEND_HOST,
        port=s.BACKEND_PORT,
        reload=False if s.PROD_ENVIRONMENT else True,
    )
