from typing import Callable

from core.connections import tcp_connection
from core.config import settings as s
from core.log import logger
from devices.base import BaseDeviceDriver
from validators.response import ResponseTypes, DeviceResponse, ScalesResponse


class BaseScaleDriver(BaseDeviceDriver):
    """Базовый класс драйверов весов."""

    def __init__(self, command: bytes | None, decode_response_func: Callable | None) -> None:
        """Инициализация объекта класса."""
        self.decode_response_func = decode_response_func
        super().__init__(command)

    async def run_scales_exchange(self, host: str, port: int, websocket_id: str) -> DeviceResponse:
        """Отправляем команду (если требуется) и получаем ответ по TCP."""
        try:
            # Получаем TCP соединение или создаем новое
            reader, writer = await tcp_connection.get_or_create(host, port, websocket_id)

            # Если устройство ожидает запрос, отправляем его
            if self.command:
                await self.send_to_device(host, port, self.command, writer, websocket_id)

            # Получаем ответ устройства
            response = await self.receive_from_device(host, port, reader, websocket_id)

            # Если устройство закрыло соединение или не ответило — удаляем соединение из пула
            if not response:
                await self.stop_exchange(host, port, websocket_id)
                return DeviceResponse(device=(host, port), ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_CONNECTION_CLOSED)

            response_decoded: ScalesResponse | None = self.decode_response_func(response)

            if response_decoded is None:
                return DeviceResponse(device=(host, port), ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_RESPONSE_VALIDATION)

            # Возвращаем серверу ответ устройства
            return DeviceResponse(device=(host, port), ok=True, type=ResponseTypes.weight, data=response_decoded, message=None)

        except Exception as e:
            # Закрываем соединение при ошибке
            await tcp_connection.close(host, port, websocket_id)
            logger.error(f'<{websocket_id}> ❌  Ошибка при обмене с {host}:{port}: {e}')
            return DeviceResponse(device=(host, port), ok=False, type=ResponseTypes.error, data=None, message=str(e))
