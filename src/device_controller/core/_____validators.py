from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.networks import IPvAnyAddress

from devices.scales.drivers import get_driver


class Commands(Enum):
    """Енум-класс для команд, обрабатываемых веб-сервером."""
    stream = 'stream'
    get = 'get'
    stop = 'stop'
    status = 'status'


class ResponseTypes(Enum):
    """Енум-класс для типов ответа сервера."""
    weight = 'weight'
    info = 'info'
    error = 'error'


class ClientRequest(BaseModel):
    """Класс для валидации и сериализации запросов от клиента."""
    command: Commands
    ip: IPvAnyAddress
    port: int = Field(ge=1024, le=65535)
    driver: Any

    @field_validator('driver', mode='before')
    @classmethod
    def find_driver(cls, value: str) -> Any:
        """."""
        return get_driver(value)

    @property
    def device_socket(self) -> tuple[str, int]:
        """Возвращаем сокет устройства из запроса."""
        return (self.ip.compressed, self.port)


class ScalesWeightResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе устройства серверу."""
    weight: float
    stable: bool
    overload: bool


class ScalesResponse(BaseModel):
    """Класс для валидации и сериализации ответов устройства серверу."""
    ok: bool
    type: ResponseTypes
    data: ScalesWeightResponse | None = None
    message: str | None = None


class ServerResponse(BaseModel):
    """Класс для валидации и сериализации ответов сервера клиенту."""
    ok: bool
    type: ResponseTypes
    data: ScalesWeightResponse | None = None
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)
