import asyncio

from core.log import L, logger
from core.config import settings as s

from device_controller.connections import tcp_connection
from device_controller.validators import ResponseTypes, DeviceResponse


class BaseDeviceDriver:
    """Базовый класс драйверов конечных устройств."""

    def _encode_command_func(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _encode_load_font_func(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def _encode_load_image_func(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    def load_font(self, *args, **kwargs) -> None:
        """Реализуется в дочерних классах."""
        raise NotImplementedError(s.MESSAGE_METHOD_NOT_IMPLEMENTED)

    async def __send(self, host: str, port: int, command: bytes, writer: asyncio.StreamWriter) -> None:
        """Отправляем пакет на устройство по TCP."""
        writer.write(command)
        await writer.drain()
        logger.log(L.DEVICES, f'➡️  {host}:{port}: {command}')

    async def __receive(self, host: str, port: int, reader: asyncio.StreamReader) -> bytes:
        """Получаем ответ от устройства по TCP."""
        response = await asyncio.wait_for(
            reader.read(s.DEVICE_RESPONSE_SIZE_BYTES), timeout=s.CONNECT_TO_DEVICE_TIMEOUT)
        logger.log(L.DEVICES, f'⬅️  {host}:{port}: {response}')
        return response

    async def _send_workflow(self, host: str, port: int, command_bytes: bytes) -> DeviceResponse:
        """Реализуем цикл отправки команды на устройство, без ожидания ответа."""
        try:
            # Получаем TCP соединение или создаем новое
            _, writer = await tcp_connection.get_or_create(host, port)

            # Отправляем команду на устройство
            await self.__send(host, port, command_bytes, writer)

            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except asyncio.TimeoutError:
            logger.error(f'❌  Ответ от {host}:{port} не получен, превышен таймаут')
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=s.MESSAGE_DEVICE_RESPONSE_TIMEOUT)

        except Exception as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        finally:
            await tcp_connection.close(host, port)

    async def _send_and_receive_workflow(self, host: str, port: int, command_bytes: bytes) -> DeviceResponse:
        """Реализуем цикл отправки команды на устройство, получаем ответ."""
        try:
            # Получаем TCP соединение или создаем новое
            reader, writer = await tcp_connection.get_or_create(host, port)

            # Отправляем команду на устройство
            await self.__send(host, port, command_bytes, writer)

            # Получаем ответ от устройства
            response: bytes = await self.__receive(host, port, reader)

            return DeviceResponse(ok=True, type=ResponseTypes.data, data=response, message=s.MESSAGE_COMMAND_SENT_SUCCESS)

        except asyncio.TimeoutError:
            logger.error(f'❌  Ответ от {host}:{port} не получен, превышен таймаут')
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=s.MESSAGE_DEVICE_RESPONSE_TIMEOUT)

        except Exception as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            return DeviceResponse(ok=False, type=ResponseTypes.error, data=None, message=str(e))

        finally:
            await tcp_connection.close(host, port)

    async def test_connection(self, host: str, port: int) -> DeviceResponse:
        """Проверяем доступность устройства по TCP."""
        try:
            # Пытаемся создать соединение
            await tcp_connection.create(host, port)
            return DeviceResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_CONNECTION_SUCCESSFUL)

        except Exception as e:
            logger.error(f'❌  Ошибка при обмене с {host}:{port}: {str(e)}')
            return DeviceResponse(ok=False, type=ResponseTypes.info, data=None, message=str(e))

        finally:
            await tcp_connection.close(host, port)
