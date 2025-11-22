from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.networks import IPvAnyAddress

from devices.base import BaseDeviceClient
from devices.scales.drivers import get_driver


class Commands(Enum):
    """Енум-класс для команд, обрабатываемых веб-сервером."""
    stream = 'stream'
    get = 'get'
    stop = 'stop'
    status = 'status'


class ClientRequest(BaseModel):
    """Класс для валидации и сериализации запросов от клиента."""
    command: Commands
    ip: IPvAnyAddress
    port: int = Field(ge=1024, le=65535)
    driver: BaseDeviceClient

    @field_validator('driver', mode='before')
    @classmethod
    def find_driver(cls, value: str) -> BaseDeviceClient:
        """Ищем запрошенный драйвер, возвращаем его в атрибут объекта модели."""
        return get_driver(value)

    @property
    def device_socket(self) -> tuple[str, int]:
        """Возвращаем сокет устройства из запроса."""
        return (self.ip.compressed, self.port)

    model_config = ConfigDict(arbitrary_types_allowed=True)
