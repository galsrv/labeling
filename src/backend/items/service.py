from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_service import BaseService
from core.config import settings as s
from items.models import ItemsOrm


class ItemsService(BaseService):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ItemsOrm)

    async def get_all_items(
        self,
        session: AsyncSession,
    ) -> list[ItemsOrm]:
        """Получаем все продукты."""
        items = await self.get_all(session)
        return items

    async def get_item(
        self,
        session: AsyncSession,
        item_id: int,
    ) -> ItemsOrm:
        """Получаем продукт."""
        item: ItemsOrm | None = await self.get(session, item_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        return item


items_service = ItemsService()
