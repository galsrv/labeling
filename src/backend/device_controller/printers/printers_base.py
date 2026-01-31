from device_controller.base import BaseDeviceDriver
from device_controller.validators import ResponseTypes, DeviceResponse


class BasePrinterDriver(BaseDeviceDriver):
    """Базовый класс драйверов принтеров."""

    async def print_label(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем этикетку на печать."""
        # Кодируем команду на основании драйвера
        try:
            command_bytes: bytes = self._encode_command_func(command)
        except NotImplementedError as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        return await self._send_workflow(host, port, command_bytes)

    async def load_font(self, host: str, port: int, font_file_bytes: bytes, filename: str, font_id: int) -> DeviceResponse:
        """Загружаем штрифт в принтер."""
        try:
            # Кодируем команду на основании драйвера
            command_bytes: bytes = self._encode_load_font_func(font_file_bytes, filename, font_id)
        except NotImplementedError as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        return await self._send_workflow(host, port, command_bytes)

    async def load_image(self, host: str, port: int, image_file_bytes: bytes, filename: str) -> DeviceResponse:
        """Загружаем картинку в принтер."""
        try:
            # Кодируем команду на основании драйвера
            command_bytes: bytes = self._encode_load_image_func(image_file_bytes, filename)
        except NotImplementedError as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        return await self._send_workflow(host, port, command_bytes)

    async def send_arbitrary_command(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем произвольную комунду на принтер."""
        # Кодируем команду на основании драйвера
        try:
            command_bytes: bytes = self._encode_command_func(command)
        except NotImplementedError as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        return await self._send_and_receive_workflow(host, port, command_bytes)
