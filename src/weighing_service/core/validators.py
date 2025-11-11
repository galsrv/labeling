from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.networks import IPvAnyAddress


class Commands(Enum):
    """Енум-класс для команд, обрабатываемых веб-сервером."""
    start = 'start'
    stop = 'stop'


class ResponseTypes(Enum):
    """Енум-класс для типов ответа сервера."""
    weight = 'weight'
    info = 'info'
    error = 'error'


class ServerRequest(BaseModel):
    """Класс для валидации и сериализации запросов от клиента."""
    command: Commands
    ip: IPvAnyAddress
    port: int = Field(ge=1024, le=65535)
    model: str


class ScalesWeightResponse(BaseModel):
    """Класс для валидации и сериализации блока данных в ответе весов серверу."""
    weight: float
    stable: bool
    overload: bool


class ScalesResponse(BaseModel):
    """Класс для валидации и сериализации ответов весов серверу."""
    ok: bool
    type: ResponseTypes
    data: ScalesWeightResponse | None = None
    message: str | None = None


class ServerResponse(BaseModel):
    """Класс для валидации и сериализации ответов сервера клиенту."""
    ok: bool
    type: ResponseTypes
    data: dict[str, Any] | None = None
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)
