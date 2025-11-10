from asyncio import open_connection, wait_for
import asyncio

from loguru import logger

from core.config import settings as s
from scales.base import BaseWeightClient
from scales.tenzo_m.utils import decode_weight_frame

class TensoM(BaseWeightClient):
    '''
    Класс с реализацией протокола Тензо-М.
    Команды-запросы формируются как FF Adr COP CRC FF FF, всего 6 байт.
    Adr = Адрес, 1 байт, обычно 1
    COP = Код операции, 1 байт
    CRC = Контрольное значение, считается на основании Adr + CRC, для расчета есть метод
    Для используемых команд значения CRC заранее рассчитаны
    '''
    __get_gross_command =   b'\xFF\x01\xC3\xE3\xFF\xFF'
    __get_net_command =     b'\xFF\x01\xC2\x8A\xFF\xFF'
    __set_tare_command =    b'\xFF\x01\xC0\x58\xFF\xFF'
    __response_size_bytes = 100

    def __init__(self):
        """Создаем словарь с активными подключениям к весам."""
        self._connections: dict[tuple[str, int], tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

    async def __get_connection(self, host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Возвращает активное TCP соединение, открывает новое при необходимости."""
        scales_socket = (host, port)

        # Если соединение уже есть — проверяем, живо ли оно
        if scales_socket in self._connections:
            reader, writer = self._connections[scales_socket]
            if not writer.is_closing():
                return reader, writer
            else:
                logger.warning(f"🔄 Соединение с {host}:{port} закрыто, пересоздаем")
                del self._connections[scales_socket]

        # Создаем новое соединение
        try:
            reader, writer = await wait_for(open_connection(host, port), timeout=s.GET_WEIGHT_TIMEOUT)
            
            self._connections[scales_socket] = (reader, writer)
            logger.info(f"⚡ Открыто новое соединение с {host}:{port}")
            return reader, writer
        except Exception as e:
            logger.error(f"❌ Не удалось установить соединение с {host}:{port}: {e}")
            raise

    async def close_connection(self, host: str, port: int):
        """Закрываем соединение."""
        scales_socket = (host, port)
        conn = self._connections.pop(scales_socket, None)
        if conn:
            _, writer = conn
            writer.close()
            await writer.wait_closed()
            logger.info(f"🔒 Соединение с {host}:{port} закрыто")

    async def close_all_connections(self):
        """Закрываем все активные соединения (например, при завершении сервера)."""
        for (host, port), (_, writer) in self._connections.items():
            writer.close()
            await writer.wait_closed()
            logger.info(f"🔚 Закрыто соединение с весами {host}:{port}")
        self._connections.clear()

    async def __send_command(self, host: str, port: int, command: bytes) -> dict:
        """Отправляем команду и получаем ответ по постоянному TCP соединению."""
        try:
            reader, writer = await self.__get_connection(host, port)
            writer.write(command)
            await writer.drain()
            logger.debug(f"⚖️  → {host}:{port}: {command}")

            response = await wait_for(reader.read(self.__response_size_bytes), timeout=s.GET_WEIGHT_TIMEOUT)
            logger.debug(f"⚖️  ← {host}:{port}: {response}")

            # Если весы закрыли соединение — удалить из пула
            if not response:
                await self.close_connection(host, port)
                return {'error': 'Пустой ответ, соединение закрыто'}

            return {'data': response}

        except Exception as e:
            # Если ошибка — попробуем закрыть соединение, чтобы в следующий раз пересоздать
            await self.close_connection(host, port)
            logger.error(f"⚠️  Ошибка при обмене с {host}:{port}: {e}")
            return {'error': str(e)}

    async def set_tare(self, host: str, port: int) -> dict:
        await self.__send_command(host, port, self.__set_tare_command)
        return {'OK': True}

    async def get_gross_weight(self, host: str, port: int) -> dict:
        response = await self.__send_command(host, port, self.__get_gross_command)
        if 'error' in response:
            return response

        decoded = decode_weight_frame(response['data'])
        if decoded is None:
            return {'error': s.ERROR_RESPONSE_VALIDATION}

        weight, stable, overload = decoded
        return {'gross': weight, 'stable_flag': stable, 'overload_flag': overload}

    async def get_net_weight(self, host: str, port: int) -> dict:
        response = await self.__send_command(host, port, self.__get_net_command)
        if 'error' in response:
            return response

        decoded = decode_weight_frame(response['data'])
        if decoded is None:
            return {'error': s.ERROR_RESPONSE_VALIDATION}

        weight, stable, overload = decoded
        return {'net': weight, 'stable_flag': stable, 'overload_flag': overload}


    # async def send_command111(self, host: str, port: int, command: bytes) -> dict:
    #     '''Метод асинхронного взаимодействия с весами.'''
    #     try:
    #         # Устанавливаем соединение по TCP, отправляем запрос
    #         reader, writer = await wait_for(open_connection(host, port), timeout=s.GET_WEIGHT_TIMEOUT)
    #         writer.write(command)
    #         await writer.drain()
    #         logger.info(f'⚖️  Запрос к {host}:{port}: {command}')

    #         # Получаем ответ
    #         response = await wait_for(reader.read(self.__response_size_bytes), timeout=s.GET_WEIGHT_TIMEOUT)
    #         logger.info(f'⚖️  Ответ от {host}:{port}: {response}')

    #         # Закрываем соединение
    #         writer.close()
    #         await wait_for(writer.wait_closed(), timeout=s.GET_WEIGHT_TIMEOUT)

    #         return {'data': response}
    #     except Exception as e:
    #         return {'error': str(e)}

    # async def set_tare111(self, host: str, port: int) -> dict:
    #     '''Устанавливаем текущую тару в ноль.'''
    #     await self.send_command(host, port, self.__set_tare_command)
    #     # Ответ не разбираем
    #     return {'OK': True}

    # async def get_gross_weight111(self, host: str, port: int) -> dict:
    #     '''Получаем вес брутто с весов.'''
    #     response: dict = await self.send_command(host, port, self.__get_gross_command)

    #     if 'error' in response.keys():
    #         return response

    #     # Декодируем ответ, проверяем CRC
    #     response_decoded: tuple | None = decode_weight_frame(response['data'])

    #     if response_decoded is None:
    #         return {'error': s.ERROR_RESPONSE_VALIDATION}

    #     weight, stable, overload = response_decoded
    #     return {'gross': weight, 'stable_flag': stable, 'overload_flag': overload}

    # async def get_net_weight111(self, host: str, port: int) -> dict:
    #     '''Получаем вес нетто с весов.'''
    #     response: dict = await self.send_command(host, port, self.__get_net_command)

    #     if 'error' in response.keys():
    #         return response

    #     # Декодируем ответ, проверяем CRC
    #     response_decoded: tuple | None = decode_weight_frame(response['data'])

    #     if response_decoded is None:
    #         return {'error': s.ERROR_RESPONSE_VALIDATION}

    #     weight, stable, overload = response_decoded
    #     return {'net': weight, 'stable_flag': stable, 'overload_flag': overload}





weight_service_tenso_m = TensoM()