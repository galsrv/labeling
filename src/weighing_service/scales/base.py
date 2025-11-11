import abc

from core.validators import ScalesResponse


class BaseWeightClient(abc.ABC):
    """Базовый класс драйверов весов."""

    @abc.abstractmethod
    async def get_gross_weight(self, *args, **kwargs) -> ScalesResponse:
        """Абстрактный метод отправки команды получения веса брутто."""
        raise NotImplementedError()
