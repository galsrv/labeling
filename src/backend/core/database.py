from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings as s

class PreBase:
    """Базовый класс для всех моделей ORM."""
    __abstract__ = True

AppBaseClass = declarative_base(cls=PreBase)

engine = create_async_engine(
    url=s.DATABASE_URL, echo=False if s.PROD_ENVIRONMENT else True
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session