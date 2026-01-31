from enum import Enum

from pydantic import BaseModel


class ResponseTypes(Enum):
    """Енум-класс для типов ответа сервера."""
    data = 'data'
    info = 'info'
    error = 'error'
    # status = 'status'


class ScalesResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе весов серверу."""
    weight: float
    stable: bool
    overload: bool


class PrinterResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе принтера серверу."""
    response: str


class DeviceResponse(BaseModel):
    """Класс для валидации и сериализации ответов устройства серверу."""
    # device: tuple[str, int]
    ok: bool
    type: ResponseTypes
    data: str | None = None
    message: str
    # data: ScalesResponse | PrinterResponse | str | None = None
    # message: str | None = None
