from core.config import settings as s

from device_drivers.base import BaseDeviceDriver
from device_drivers.validators import ResponseTypes, DeviceResponse


class BasePrinterDriver(BaseDeviceDriver):
    """Базовый класс драйверов принтеров."""

    def _decode_response(self, response_bytes: bytes) -> str:
        response_str = response_bytes.decode('utf-8', errors='replace')
        return response_str

    async def print_label(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем этикетку на печать.

        1. Кодируем команду
        2. Отправляем команду.
        """
        try:
            command_bytes: bytes = self._encode_command(command)
            await self._send_workflow(host, port, command_bytes)
            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e) or s.MESSAGE_COMMAND_SENT_FAIL)

    async def load_font(self, host: str, port: int, font_file_bytes: bytes, filename: str, font_id: int) -> DeviceResponse:
        """Загружаем штрифт в принтер.

        1. Кодируем команду
        2. Отправляем команду.
        """
        try:
            command_bytes: bytes = self._encode_load_font(font_file_bytes, filename, font_id)
            await self._send_workflow(host, port, command_bytes)
            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

    async def load_image(self, host: str, port: int, image_file_bytes: bytes, filename: str) -> DeviceResponse:
        """Загружаем картинку в принтер.

        1. Кодируем команду
        2. Отправляем команду.
        """
        try:
            command_bytes: bytes = self._encode_load_image(image_file_bytes, filename)
            await self._send_workflow(host, port, command_bytes)
            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

    async def send_arbitrary_command(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем произвольную комунду на принтер.

        1. Кодируем команду
        2. Отправляем команду, получаем ответ
        3. Декодируем ответ.
        """
        try:
            command_bytes: bytes = self._encode_command(command)
            response_bytes: bytes = await self._send_and_receive_workflow(host, port, command_bytes)
            response: str = self._decode_response(response_bytes)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

        return DeviceResponse(ok=True, type=ResponseTypes.data, data=response, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

    async def test_connection(self, host: str, port: int) -> DeviceResponse:
        """Проверяем доступность устройства по TCP."""
        test_command = self._get_test_connection_command()
        response: DeviceResponse = await self.send_arbitrary_command(host, port, test_command)
        success_flag: bool = self._evaluate_test_connection(response.data) if response.ok else False
        return DeviceResponse(ok=success_flag, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS if success_flag else s.MESSAGE_CONNECTION_FAILED)
