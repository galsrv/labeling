from sqlalchemy.ext.asyncio import AsyncSession

from items.repository import items_repo
from items.schemas import ItemReadSchema


class ItemsService:
    """Сервисный слой для продуктов."""
    async def get_all(self, session: AsyncSession) -> list[ItemReadSchema]:
        """Возвращаем из БД все продукты."""
        items = await items_repo.get_all(session)
        items_dto = [ItemReadSchema.model_validate(item) for item in items]
        return items_dto

    async def get(self, session: AsyncSession, item_id: int) -> ItemReadSchema:
        """Возвращаем из БД продукт по его id."""
        item = await items_repo.get(session, item_id)
        item_dto = ItemReadSchema.model_validate(item)
        return item_dto

    async def get_all_gtins(self, session: AsyncSession) -> list:
        """Метод получения всех значений поля GTIN."""
        return await items_repo.get_all_gtins(session)


items_service = ItemsService()
