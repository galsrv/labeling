from typing import Callable

from devices.base import BaseDeviceDriver
from validators.base import DeviceTypes


class BasePrinterDriver(BaseDeviceDriver):
    """Базовый класс драйверов принтеров."""

    def __init__(self, command: bytes | None, decode_response_func: Callable | None, encode_print_command_func: Callable | None) -> None:
        """Инициализация объекта класса."""
        self.encode_print_command_func = encode_print_command_func
        self.decode_response_func = decode_response_func
        self.expect_response: bool = False
        super().__init__(
            command=command,
            device_type=DeviceTypes.printer,
        )
