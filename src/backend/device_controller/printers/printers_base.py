from core.config import settings as s

from device_controller.base import BaseDeviceController
from device_controller.validators import ResponseTypes, DeviceResponse


class BasePrinterController(BaseDeviceController):
    """Базовый класс драйверов принтеров."""

    async def print_label(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем этикетку на печать."""
        try:
            # Кодируем команду
            command_bytes: bytes = self._encode_command(command)

            # Отправляем команду
            await self._send_workflow(host, port, command_bytes)

            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e) or s.MESSAGE_COMMAND_SENT_FAIL)

    async def load_font(self, host: str, port: int, font_file_bytes: bytes, filename: str, font_id: int) -> DeviceResponse:
        """Загружаем штрифт в принтер."""
        try:
            # Кодируем команду
            command_bytes: bytes = self._encode_load_font(font_file_bytes, filename, font_id)

            # Отправляем команду
            await self._send_workflow(host, port, command_bytes)

            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

    async def load_image(self, host: str, port: int, image_file_bytes: bytes, filename: str) -> DeviceResponse:
        """Загружаем картинку в принтер."""
        try:
            # Кодируем команду
            command_bytes: bytes = self._encode_load_image(image_file_bytes, filename)

            # Отправляем команду
            await self._send_workflow(host, port, command_bytes)

            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

    async def send_arbitrary_command(self, host: str, port: int, command: str) -> DeviceResponse:
        """Отправляем произвольную комунду на принтер."""
        try:
            # Кодируем команду
            command_bytes: bytes = self._encode_command(command)

            # Отправляем команду, получаем ответ
            response_bytes: bytes = await self._send_and_receive_workflow(host, port, command_bytes)

            # Декодируем ответ
            response: str = self._decode_response(response_bytes)

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

        return DeviceResponse(ok=True, type=ResponseTypes.data, data=response, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

    async def test_connection(self, host: str, port: int) -> DeviceResponse:
        """Проверяем доступность устройства по TCP."""
        test_command = self._get_test_connection_command()
        response: DeviceResponse = await self.send_arbitrary_command(host, port, test_command)
        success_flag: bool = self._evaluate_test_connection(response.data) if response.ok else False
        return DeviceResponse(ok=success_flag, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS if success_flag else s.MESSAGE_COMMAND_SENT_FAIL)
