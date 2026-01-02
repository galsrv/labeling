from core.base_repo import BaseRepository
from workplaces.models import DeviceDriversOrm, ScalesOrm, PrinterOrm, WorkplaceOrm


class DeviceDriversRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(DeviceDriversOrm)


class ScalesRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(ScalesOrm)


class PrintersRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(PrinterOrm)


class WorkplaceRepository(BaseRepository):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(WorkplaceOrm)


drivers_repo = DeviceDriversRepository()

scales_repo = ScalesRepository()

printers_repo = PrintersRepository()

workplaces_repo = WorkplaceRepository()
