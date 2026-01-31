from core.base_repo import BaseRepository
from workplaces.models import PrinterOrm


class PrintersRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(PrinterOrm)


printers_repo = PrintersRepository()
