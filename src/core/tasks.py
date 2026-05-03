import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from auth.tasks import cleanup_tokens_task
from core.config import settings as s
from core.log import logger


@asynccontextmanager
async def lifespan_tasks(app: FastAPI) -> AsyncGenerator:
    """Создание генератора для задачи удаления токенов."""
    task = asyncio.create_task(cleanup_tokens_task())
    logger.info(s.MESSAGE_TOKEN_CLEANUP_TASK_CREATED)
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
