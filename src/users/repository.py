from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from database.exceptions import ObjectNotFoundError
from database.repository import BaseRepository
from users.models import RolesOrm, UsersOrm


class RolesRepository(BaseRepository):
    """Класс-репозиторий модели."""
    def __init__(self) -> None:
        super().__init__(RolesOrm)


roles_repo = RolesRepository()


class UsersRepository(BaseRepository):
    """Класс-репозиторий модели."""
    def __init__(self) -> None:
        super().__init__(UsersOrm)

    async def get_by_username(self, session: AsyncSession, username: str) -> UsersOrm | None:
        """Метод поиска записи по юзернейму."""
        query = select(UsersOrm).where(UsersOrm.username == username)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        if db_obj is None:
            message = s.MESSAGE_DB_OBJECTS_GET_BY_FIELD.format(model=UsersOrm.__name__, field='username', value=username, success=bool(db_obj))
            logger.debug(message)
            raise ObjectNotFoundError(message)

        logger.debug(s.MESSAGE_DB_OBJECTS_GET_BY_FIELD.format(model=UsersOrm.__name__, field='username', value=username, success=bool(db_obj)))
        return db_obj


users_repo = UsersRepository()
