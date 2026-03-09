import asyncio

from core.log import L, logger
from core.config import settings as s

from device_drivers.connections import tcp_connection
from device_drivers.validators import ResponseTypes, DeviceResponse, NotImplementedClass


class BaseDeviceDriver(NotImplementedClass):
    """Базовый класс драйверов конечных устройств."""

    async def _create_connection(self, host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Получаем TCP соединение или создаем новое."""
        reader, writer = await tcp_connection.get_or_create(host, port)
        return reader, writer

    async def _close_connection(self, host: str, port: int) -> None:
        """Закрываем TCP соединение."""
        await tcp_connection.close(host, port)

    async def _send(self, host: str, port: int, command: bytes, writer: asyncio.StreamWriter) -> None:
        """Отправляем пакет на устройство по TCP."""
        writer.write(command)
        await asyncio.wait_for(
            writer.drain(), timeout=s.CONNECT_TO_DEVICE_TIMEOUT)

        command_cut = command if len(command) < 50 else f'{command[:30]}...{command[-30:]}'
        logger.log(L.DEVICES, f'➡️  {host}:{port}: {command_cut}')

    async def _receive(self, host: str, port: int, reader: asyncio.StreamReader) -> bytes:
        """Получаем ответ от устройства по TCP."""
        response = await asyncio.wait_for(
            reader.read(s.DEVICE_RESPONSE_SIZE_BYTES), timeout=s.CONNECT_TO_DEVICE_TIMEOUT)

        logger.log(L.DEVICES, f'⬅️  {host}:{port}: {response}')
        return response

    async def _send_workflow(self, host: str, port: int, command_bytes: bytes) -> None:
        """Реализуем цикл отправки команды на устройство, без ожидания ответа.

        1. Получаем TCP соединение или создаем новое
        2. Отправляем команду на устройство
        """
        try:
            _, writer = await self._create_connection(host, port)
            await self._send(host, port, command_bytes, writer)

        except (asyncio.TimeoutError, Exception) as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            raise

        finally:
            await self._close_connection(host, port)

    async def _send_and_receive_workflow(self, host: str, port: int, command_bytes: bytes) -> bytes:
        """Реализуем однократную отправку команды на устройство и получение ответа.

        1. Получаем TCP соединение или создаем новое
        2. Отправляем команду на устройство
        3. Получаем ответ от устройства, возвращаем
        """
        try:
            reader, writer = await self._create_connection(host, port)
            await self._send(host, port, command_bytes, writer)
            response_bytes: bytes = await self._receive(host, port, reader)
            return response_bytes

        except (asyncio.TimeoutError, Exception) as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            raise e

        finally:
            await self._close_connection(host, port)

    async def test_connection(self, host: str, port: int) -> DeviceResponse:
        """Проверяем доступность устройства по TCP."""
        try:
            # Пытаемся создать соединение
            await self._create_connection(host, port)
            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_CONNECTION_SUCCESSFUL)

        except Exception as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

        finally:
            await self._close_connection(host, port)
