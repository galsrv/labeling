import asyncio
from enum import StrEnum
from typing import AsyncIterator

from core.log import logger
from core.config import settings as s

from device_drivers.base import BaseDeviceDriver
from device_drivers.validators import DeviceResponse, ResponseTypes


class ScalesModes(StrEnum):
    """Режимы работы весов.

    pull - весы отвечают на запрос
    push - весы отправляют данные в потоке (стартовая команда может не требоваться)
    """
    pull = 'pull'
    push = 'push'


class BaseScalesDriver(BaseDeviceDriver):
    """Базовый класс драйверов весов.

    Режим работы весов по умолчанию - pull (по запросу).
    """
    def __init__(self) -> None:
        self.mode = ScalesModes.pull
        super().__init__()

    async def get_weight(self, host: str, port: int) -> DeviceResponse:
        """Получаем вес с весов однократно."""
        command_bytes: bytes | None = self._get_gross_weight_command()

        if command_bytes is None:
            pass  # Написать когда буду работать с весами без стартовой команды

        try:
            response_bytes: bytes = await self._send_and_receive_workflow(host, port, command_bytes)
            response: DeviceResponse = self._decode_response(response_bytes)
            return response

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))

    async def get_weight_stream(self, host: str, port: int) -> AsyncIterator[DeviceResponse]:
        """Получаем вес с весов в цикле. Используем объект-генератор."""
        command_bytes: bytes | None = self._get_gross_weight_command()

        if command_bytes is None:
            pass  # Написать когда буду работать с весами без стартовой команды

        try:
            async for response_bytes in self._send_and_receive_stream(host, port, command_bytes):
                response: DeviceResponse = self._decode_response(response_bytes)
                yield response

        except Exception as e:
            yield DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))
            return

    async def _send_and_receive_stream(self, host: str, port: int, command_bytes: bytes) -> AsyncIterator[bytes]:
        """Реализуем цикл запросов/ответов устройства.

        Функция представляет собой генератор.
        Реализуем разную последовательность действий для разных режимов работы весов.
        """
        try:
            reader, writer = await self._create_connection(host, port)

            if self.mode == ScalesModes.pull:
                while True:
                    await self._send(host, port, command_bytes, writer)
                    yield await self._receive(host, port, reader)
                    await asyncio.sleep(s.DEVICE_POLL_INTERVAL)

            else:
                await self._send(host, port, command_bytes, writer)
                while True:
                    yield await self._receive(host, port, reader)

        except (asyncio.TimeoutError, Exception) as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            raise

        finally:
            await self._close_connection(host, port)
