from typing import Callable

from devices.base import BaseDeviceDriver
from validators.base import DeviceTypes


class BaseScaleDriver(BaseDeviceDriver):
    """Базовый класс драйверов весов."""

    def __init__(self, command: bytes | None, decode_response_func: Callable | None) -> None:
        """Инициализация объекта класса."""
        self.decode_response_func = decode_response_func
        super().__init__(
            command=command,
            device_type=DeviceTypes.scales,
        )
