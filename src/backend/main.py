import uvicorn
from fastapi import FastAPI

from core.config import settings as s
from core.routers import main_router

fastapi_app = FastAPI(
    title=s.APP_TITLE,
    openapi_url=s.OPENAPI_URL,
    docs_url=s.DOCS_URL,
    redoc_url=s.REDOC_URL
)

fastapi_app.include_router(main_router)

if __name__ == '__main__':
    uvicorn.run(
        'main:fastapi_app',
        host=s.HOST,
        port=s.PORT,
        reload=False if s.PROD_ENVIRONMENT else True,
    )
