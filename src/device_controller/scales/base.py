import asyncio
from typing import Callable

from core.connections import scale_connections
from core.config import settings as s
from core.log import L, logger
from device_controller.core._____validators import ResponseTypes, ScalesResponse, ScalesWeightResponse


class BaseDeviceClient:
    """Базовый класс драйверов конечных устройств."""

    def __init__(self, get_gross_weight_command: str | None, decode_response_func: Callable) -> None:
        """Инициализация объекта класса."""
        self.get_gross_weight_command = get_gross_weight_command
        self.decode_response_func = decode_response_func
        self.response_size_bytes = 20

    async def send_request_to_device(self, host: str, port: int, command: bytes, writer: asyncio.StreamWriter, websocket_id: str) -> None:
        """Отправляем запрос на устройство по TCP."""
        writer.write(command)
        await writer.drain()
        logger.log(L.SCALES, f'<{websocket_id}> → {host}:{port}: {command}')

    async def get_response_from_device(self, host: str, port: int, reader: asyncio.StreamReader, websocket_id: str) -> bytes:
        """Получаем ответ от устройства по TCP."""
        response = await asyncio.wait_for(reader.read(self.response_size_bytes), timeout=s.GET_WEIGHT_TIMEOUT)
        logger.log(L.SCALES, f'<{websocket_id}> ← {host}:{port}: {response}')

        return response

    async def exchange(self, host: str, port: int, websocket_id: str) -> ScalesResponse:
        """Отправляем команду (если требуется) и получаем ответ по TCP."""
        try:
            # Получаем TCP соединение или создаем новое
            reader, writer = await scale_connections.get(host, port, websocket_id)

            # Если устройство ожидает запрос, отправляем его
            if self.get_gross_weight_command:
                await self.send_request_to_device(host, port, self.get_gross_weight_command, writer, websocket_id)

            # Получаем ответ устройства
            response = await self.get_response_from_device(host, port, reader, websocket_id)

            # Если устройство закрыло соединение — удаляем соединение из пула
            if not response:
                await scale_connections.close(host, port, websocket_id)
                return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_CONNECTION_CLOSED)

            response_decoded: ScalesWeightResponse | None = self.decode_response_func(response)

            if response_decoded is None:
                return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_RESPONSE_VALIDATION)

            # Возвращаем серверу декодированный ответ устройства
            return ScalesResponse(ok=True, type=ResponseTypes.weight, data=response_decoded, message=None)

        except Exception as e:
            # Закрываем соединение при ошибке
            await scale_connections.close(host, port, websocket_id)
            logger.error(f'<{websocket_id}> ❌  Ошибка при обмене с {host}:{port}: {e}')
            return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))
