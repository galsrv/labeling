from typing import AsyncGenerator, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core.config import settings as s


class PreBase:
    """Базовый класс для всех моделей ORM."""
    __abstract__ = True


AppBaseClass = declarative_base(cls=PreBase)


class ORMBase(Protocol):
    """Базовый класс для корректной проверки типов."""
    id: int

    __order_by__ = (id, )


# Класс для проверки типов
TOrm = TypeVar("TOrm", bound=ORMBase)


engine = create_async_engine(
    url=s.DATABASE_URL, echo=False if s.PROD_ENVIRONMENT else True
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращаем асинхронную сессию."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
