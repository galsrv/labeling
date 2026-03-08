from enum import Enum

from pydantic import BaseModel

from core.config import settings as s


class ResponseTypes(Enum):
    """Енум-класс для типов ответа сервера."""
    data = 'data'
    info = 'info'
    error = 'error'


class ScalesResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе весов серверу."""
    weight: float
    stable: bool
    overload: bool


# class PrinterResponse(BaseModel):
#     """Класс для валидации и сериализации блока данных в ответе принтера серверу."""
#     response: str


class DeviceResponse(BaseModel):
    """Класс для валидации и сериализации ответов устройства серверу."""
    # device: tuple[str, int]
    ok: bool
    type: ResponseTypes
    data: str | ScalesResponse | None = None
    message: str | None = None


class NotImplementedClass():
    """Класс методов, требующих переопределения."""

    def _encode_command(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _encode_load_font(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _encode_load_image(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def load_font(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _get_default_command(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _get_test_connection_command(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _evaluate_test_connection(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _get_gross_weight_command(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _decode_response(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)
