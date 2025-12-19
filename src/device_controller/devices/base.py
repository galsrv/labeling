import asyncio

from core.connections import tcp_connection
from core.config import settings as s
from core.log import L, logger


class BaseDeviceDriver:
    """Базовый класс драйверов конечных устройств."""

    def __init__(self, command: bytes | None) -> None:
        """Инициализация объекта класса."""
        self.command = command

    async def send_to_device(self, host: str, port: int, command: bytes, writer: asyncio.StreamWriter, websocket_id: str) -> None:
        """Отправляем запрос на устройство по TCP."""
        writer.write(command)
        await writer.drain()
        logger.log(L.SCALES, f'<{websocket_id}> ➡️  {host}:{port}: {command}')

    async def receive_from_device(self, host: str, port: int, reader: asyncio.StreamReader, websocket_id: str) -> bytes | None:
        """Получаем ответ от устройства по TCP."""
        try:
            response = await asyncio.wait_for(
                reader.read(s.DEVICE_RESPONSE_SIZE_BYTES), timeout=s.WAIT_FOR_DEVICE_RESPONSE_TIMEOUT)

            logger.log(L.SCALES, f'<{websocket_id}> ⬅️  {host}:{port}: {response}')
            return response
        except asyncio.TimeoutError:
            logger.error(f'<{websocket_id}> ❌  Ответ от {host}:{port} не получен, превышен таймаут')

    async def stop_exchange(self, host: str, port: int, websocket_id: int) -> None:
        """Останавливаем обмен с устройством."""
        await tcp_connection.close(host, port, websocket_id)
