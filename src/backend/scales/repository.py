from core.base_repo import BaseRepository
from workplaces.models import ScalesOrm


class ScalesRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ScalesOrm)


scales_repo = ScalesRepository()
