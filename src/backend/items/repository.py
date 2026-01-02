from core.base_repo import BaseRepository
from items.models import ItemsOrm


class ItemsRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ItemsOrm)


items_repo = ItemsRepository()
