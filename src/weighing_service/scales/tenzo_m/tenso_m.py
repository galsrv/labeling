from asyncio import wait_for
import asyncio

from loguru import logger

from core.connections import scale_connections
from core.config import settings as s
from core.validators import ResponseTypes, ScalesResponse, ScalesWeightResponse
from scales.base import BaseWeightClient
from scales.tenzo_m.utils import decode_weight_frame


class TensoM(BaseWeightClient):
    """Класс с реализацией протокола Тензо-М.

    Для используемых команд значения CRC заранее рассчитаны.
    """
    __get_gross_command = b'\xFF\x01\xC3\xE3\xFF\xFF'
    __get_net_command = b'\xFF\x01\xC2\x8A\xFF\xFF'
    __set_tare_command = b'\xFF\x01\xC0\x58\xFF\xFF'
    __response_size_bytes = 100

    async def __request_to_scales(self, host: str, port: int, command: bytes, writer: asyncio.StreamWriter) -> None:
        """Отправляем запрос на весы по TCP соединению."""
        writer.write(command)
        await writer.drain()
        logger.debug(f"⚖️  → {host}:{port}: {command}")

    async def __response_from_scales(self, host: str, port: int, command: bytes, reader: asyncio.StreamReader) -> bytes:
        """Получаем ответ от весов по TCP соединению."""
        response = await wait_for(reader.read(self.__response_size_bytes), timeout=s.GET_WEIGHT_TIMEOUT)
        logger.debug(f"⚖️  ← {host}:{port}: {response}")

        return response

    async def __exchange_cycle(self, host: str, port: int, command: bytes) -> ScalesResponse:
        """Отправляем команду и получаем ответ по TCP соединению. Перенести в ScaleConnectionsPool?."""
        try:
            # Получаем соединение или создаем новое
            reader, writer = await scale_connections.get(host, port)

            # Отправляем запрос весам, получаем ответ
            await self.__request_to_scales(host, port, command, writer)
            response = await self.__response_from_scales(host, port, command, reader)

            # Если весы закрыли соединение — удаляем его из пула
            if not response:
                await scale_connections.close(host, port)
                return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_CONNECTION_CLOSED)

            response_decoded: ScalesWeightResponse | None = decode_weight_frame(response)

            if response_decoded is None:
                return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_RESPONSE_VALIDATION)

            # Возвращаем серверу вес с весов
            return ScalesResponse(ok=True, type=ResponseTypes.weight, data=response_decoded, message=None)

        except Exception as e:
            # Закрываем соединение при ошибке
            await scale_connections.close(host, port)
            logger.error(f"⚠️  Ошибка при обмене с {host}:{port}: {e}")
            return ScalesResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

    async def get_gross_weight(self, host: str, port: int) -> ScalesResponse:
        """Получаем вес брутто с весов."""
        return await self.__exchange_cycle(host, port, self.__get_gross_command)


weight_service_tenso_m = TensoM()
