from core.base_repo import BaseRepository
from labels.models import LabelTemplateORM


class LabelTemplateRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(LabelTemplateORM)


label_repo = LabelTemplateRepository()
