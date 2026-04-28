import asyncio
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import delete, or_
from sqlalchemy.exc import SQLAlchemyError

from core.config import settings as s
from auth.models import RefreshTokenORM
from database.config import AsyncSessionLocal


async def cleanup_tokens_task() -> None:
    """Чистим refresh-токены с заданной периодичностью. Удаляем токены заблокированных пользователей и просроченные."""
    while True:
        async with AsyncSessionLocal() as session:
            try:
                stmt = delete(RefreshTokenORM).where(
                    or_(
                        RefreshTokenORM.user.has(is_active=False),
                        RefreshTokenORM.expires_at < datetime.now(timezone.utc),
                    )
                )
                result = await session.execute(stmt)
                await session.commit()
                logger.debug(s.MESSAGE_DB_OBJECT_DELETE_MULTI.format(model=RefreshTokenORM.__name__, number=result.rowcount))

            except SQLAlchemyError as e:
                session.rollback()
                logger.debug(s.MESSAGE_DB_OBJECT_DELETE_ERROR.format(model=RefreshTokenORM.__name__, error=str(e)))

        await asyncio.sleep(s.REFRESH_TOKEN_CLEANUP_JOB_DELAY_SECONDS)
