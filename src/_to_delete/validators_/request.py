from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.networks import IPvAnyAddress

from core.config import settings as s
from devices.base import BaseDeviceDriver
from devices.drivers import get_driver
from validators.base import Modes


class ClientRequest(BaseModel):
    """Класс для валидации и сериализации запросов от клиента."""
    mode: Modes
    ip: IPvAnyAddress
    port: int = Field(ge=s.DEVICE_PORT_MIN, le=s.DEVICE_PORT_MAX)
    driver: BaseDeviceDriver
    print_command: str | None = None

    @field_validator('driver', mode='before')
    @classmethod
    def find_driver(cls, value: str) -> BaseDeviceDriver:
        """Ищем запрошенный драйвер, возвращаем его в атрибут объекта модели."""
        return get_driver(value)

    @property
    def device_socket(self) -> tuple[str, int]:
        """Возвращаем сокет устройства из запроса."""
        return (self.ip.compressed, self.port)

    model_config = ConfigDict(arbitrary_types_allowed=True)
