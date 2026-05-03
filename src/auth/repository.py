from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import RefreshTokenORM
from auth.schemas import RefreshTokenCreateSchema
from core.config import settings as s
from core.log import logger
from database.exceptions import ObjectNotFoundError, ObjectNotModifiedError
from database.repository import BaseRepository


class RefreshTokenRepository(BaseRepository):
    """Класс-репозиторий модели."""
    def __init__(self) -> None:
        super().__init__(RefreshTokenORM)

    async def get_by_refresh_token(self, session: AsyncSession, refresh_token_hash: str) -> RefreshTokenORM | None:
        """Метод поиска записи по хэшу refresh токена."""
        query = select(RefreshTokenORM).where(RefreshTokenORM.refresh_token_hash == refresh_token_hash)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        if db_obj is None:
            message = s.MESSAGE_DB_OBJECTS_GET_BY_FIELD.format(
                model=RefreshTokenORM.__name__, field='refresh_token_hash', value=refresh_token_hash, success=bool(db_obj))
            logger.debug(message)
            raise ObjectNotFoundError(message)

        logger.debug(s.MESSAGE_DB_OBJECTS_GET_BY_FIELD.format(model=RefreshTokenORM.__name__, field='refresh_token_hash', value=refresh_token_hash, success=bool(db_obj)))
        return db_obj

    async def rotate_tokens(self, session: AsyncSession, old_token_id: int, new_token_dto: RefreshTokenCreateSchema) -> None:
        """Метод удаления старого токена и создания нового."""
        # Сначала удаляем существующий объет
        query = delete(RefreshTokenORM).where(RefreshTokenORM.id == old_token_id)
        result = await session.execute(query)

        if result.rowcount == 0:
            await session.rollback()
            message = s.MESSAGE_DB_OBJECT_DOESNT_EXIST.format(model=RefreshTokenORM.__name__, obj_id=old_token_id)
            logger.debug(message)
            raise ObjectNotFoundError(message)

        # Далее создаем новый
        new_db_obj = self.model(**new_token_dto.model_dump())
        session.add(new_db_obj)

        try:
            await session.commit()
            await session.refresh(new_db_obj)
            logger.debug(s.MESSAGE_DB_OBJECT_CREATE.format(model=self.model.__name__, obj_id=new_db_obj.id))
            logger.debug(s.MESSAGE_DB_OBJECT_DELETE.format(model=self.model.__name__, obj_id=old_token_id))

        except IntegrityError as e:
            await session.rollback()
            logger.debug(s.MESSAGE_DB_OBJECT_MODIFICATION_ERROR.format(model=self.model.__name__, error=str(e)))

            raise ObjectNotModifiedError(str(e))


tokens_repo = RefreshTokenRepository()
