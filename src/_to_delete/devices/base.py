import asyncio

from core.connections import tcp_connection
from core.config import settings as s
from core.log import L, logger

from validators.base import DeviceTypes
from validators.response import ResponseTypes, DeviceResponse, ScalesResponse


class BaseDeviceDriver:
    """Базовый класс драйверов конечных устройств."""

    def __init__(self, command: bytes | None, device_type: DeviceTypes) -> None:
        """Инициализация объекта класса."""
        self.command = command
        self.device_type = device_type

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

    async def run_exchange(self, host: str, port: int, websocket_id: str) -> DeviceResponse:
        """Отправляем команду (если требуется) и получаем ответ по TCP."""
        try:
            # Получаем TCP соединение или создаем новое
            reader, writer = await tcp_connection.get_or_create(host, port, websocket_id)

            # Далее переделать
            if not self.device_type:
                raise Exception('Не определен тип устройства')

            if self.device_type == DeviceTypes.printer:
                await self.send_to_device(host, port, self.command, writer, websocket_id)

            # Далее переделать
            if self.device_type == DeviceTypes.scales:
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

    async def send(self, host: str, port: int, websocket_id: str, print_command: str) -> DeviceResponse:
        """Отправляем команду на устройство, ответ не требуется."""
        try:
            # Получаем TCP соединение или создаем новое
            _, writer = await tcp_connection.get_or_create(host, port, websocket_id)

            print_command_bytes = self.encode_print_command_func(print_command)

            # Отправляем запрос
            await self.send_to_device(host, port, print_command_bytes, writer, websocket_id)

        except Exception as e:
            # Закрываем соединение при ошибке
            await tcp_connection.close(host, port, websocket_id)
            logger.error(f'<{websocket_id}> ❌  Ошибка при обмене с {host}:{port}: {e}')
            return DeviceResponse(device=(host, port), ok=False, type=ResponseTypes.error, data=None, message=str(e))
