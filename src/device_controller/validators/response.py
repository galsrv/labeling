from enum import Enum

from pydantic import BaseModel, ConfigDict


class ResponseTypes(Enum):
    """Енум-класс для типов ответа сервера."""
    weight = 'weight'
    info = 'info'
    error = 'error'
    status = 'status'


class ScalesWeightResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе устройства серверу."""
    weight: float
    stable: bool
    overload: bool


class ScalesResponse(BaseModel):
    """Класс для валидации и сериализации ответов устройства серверу."""
    device: tuple[str, int]
    ok: bool
    type: ResponseTypes
    data: ScalesWeightResponse | None = None
    message: str | None = None


class ServerResponse(BaseModel):
    """Класс для валидации и сериализации ответов сервера клиенту."""
    device: tuple[str, int]
    ok: bool
    type: ResponseTypes
    data: ScalesWeightResponse | None = None
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)
