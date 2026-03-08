from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from items.repository import items_repo
from items.schemas import ItemReadSchema, ItemWebSchema

T = TypeVar('T', bound=BaseModel)


class ItemsService:
    """Сервисный слой для продуктов."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все продукты."""
        items = await items_repo.get_all(session)
        items_dto = [self.read_model.model_validate(item) for item in items]
        return items_dto

    async def get(self, session: AsyncSession, item_id: int) -> T:
        """Возвращаем из БД продукт по его id."""
        item = await items_repo.get(session, item_id)

        if item is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        item_dto = self.read_model.model_validate(item)
        return item_dto


api_items_service = ItemsService(read_model=ItemReadSchema)

web_items_service = ItemsService(read_model=ItemWebSchema)
