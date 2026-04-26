from database.repository import BaseRepository
from workplaces.models import WorkplaceOrm


class WorkplaceRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(WorkplaceOrm)


workplaces_repo = WorkplaceRepository()
