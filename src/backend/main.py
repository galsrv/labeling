import uvicorn
from fastapi import FastAPI

from core.config import settings as s
from core.exceptions import register_exception_handlers
from core.log import logger
from core.routers import api_router, web_router

fastapi_app = FastAPI(
    title=s.APP_TITLE,
    openapi_url=s.OPENAPI_URL,
    docs_url=s.DOCS_URL,
    redoc_url=s.REDOC_URL
)

fastapi_app.include_router(api_router)
fastapi_app.include_router(web_router)

register_exception_handlers(fastapi_app)

if __name__ == '__main__':
    logger.info(f'Сервер FastAPI запущен на {s.HOST}:{s.PORT}')

    uvicorn.run(
        'main:fastapi_app',
        host=s.HOST,
        port=s.PORT,
        reload=False if s.PROD_ENVIRONMENT else True,
    )
