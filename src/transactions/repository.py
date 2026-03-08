from core.base_repo import BaseRepository
from transactions.models import OrderOrm


class OrdersRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(OrderOrm)


orders_repo = OrdersRepository()
