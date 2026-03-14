import asyncio
from typing import AsyncIterator

from core.log import logger
from core.config import settings as s

from device_drivers.base import BaseDeviceDriver
from device_drivers.utils import read_fixed_length
from device_drivers.validators import DeviceResponse, ResponseTypes, ScalesModes, ScalesResponse


class BaseScalesDriver(BaseDeviceDriver):
    """Базовый класс драйверов весов.

    Атрибуты:
        _mode - Режим работы весов pull/push (по умолчанию pull - по запросу).
        _get_gross_weight_command - Команда запроса веса
        _frame_reader - Порядок разбора фрейма в ответе
        _decode_response - Функция декодирования ответа устройства
    """
    def __init__(self) -> None:
        super().__init__()

        self._mode = ScalesModes.pull
        self._get_gross_weight_command = None
        self._frame_reader_func = read_fixed_length
        self._decode_response_func = None

    def _decode_response(self, response_bytes: bytes) -> DeviceResponse:
        """Декодируем ответ весов.

        Применяем функцию-декодер, заданную в атрибуте _decode_response_func.
        """
        response: ScalesResponse | None = getattr(self, '_decode_response_func', None)(response_bytes)

        if response is None:
            return DeviceResponse(ok=False, type=ResponseTypes.error, message=s.MESSAGE_ERROR_DECODING_DEVICE_RESPONSE)

        return DeviceResponse(ok=True, type=ResponseTypes.data, data=response)

    async def get_weight(self, host: str, port: int) -> DeviceResponse:
        """Получаем вес с весов однократно."""
        command_bytes: bytes | None = getattr(self, '_get_gross_weight_command', None)

        try:
            response_bytes: bytes = await self._send_and_receive_workflow(host, port, command_bytes)
            response: DeviceResponse = self._decode_response(response_bytes)
            return response

        except Exception as e:
            return DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))

    async def get_weight_stream(self, host: str, port: int) -> AsyncIterator[DeviceResponse]:
        """Получаем вес с весов в цикле. Используем объект-генератор."""
        command_bytes: bytes | None = getattr(self, '_get_gross_weight_command', None)

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

        Если команда запроса веса не указана, пропускаем шаг отправки команды.
        """
        try:
            reader, writer = await self._create_connection(host, port)

            if self._mode == ScalesModes.pull:
                while True:
                    await self._send(host, port, command_bytes, writer)
                    yield await self._receive(host, port, reader)
                    await asyncio.sleep(s.DEVICE_POLL_INTERVAL)

            else:
                await self._send(host, port, command_bytes, writer)
                while True:
                    yield await self._receive(host, port, reader)

        except asyncio.TimeoutError as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {s.MESSAGE_DEVICE_RESPONSE_TIMEOUT}')
            raise e

        except Exception as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            raise e

        finally:
            await self._close_connection(host, port)
