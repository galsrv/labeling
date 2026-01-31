from core.base_repo import BaseRepository
from workplaces.models import ScalesOrm, WorkplaceOrm


class ScalesRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ScalesOrm)


class WorkplaceRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(WorkplaceOrm)


scales_repo = ScalesRepository()

workplaces_repo = WorkplaceRepository()
