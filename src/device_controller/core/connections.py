import asyncio

from core.config import settings as s
from core.log import L, logger


class TcpConnection:
    """Синглтон-класс для работы с TCP-подключениями к устройствам."""
    _connections: dict[tuple[str, int], tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

    @classmethod
    def get(cls, host: str, port: int, websocket_id: str) -> tuple[asyncio.StreamReader | None, asyncio.StreamWriter | None]:
        """Возвращает активное TCP соединение c устройством, если таковое есть."""
        scales_socket = (host, port)

        if scales_socket in cls._connections:
            reader, writer = cls._connections[scales_socket]

            if not writer.is_closing():
                return reader, writer

            del cls._connections[scales_socket]

        return None, None

    @classmethod
    async def create(cls, host: str, port: int, websocket_id: str) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Открываем новоем TCP соединение c устройством."""
        scales_socket = (host, port)

        for _ in range(s.CONNECT_TO_DEVICE_ATTEMPTS):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=s.CONNECT_TO_DEVICE_TIMEOUT)

                cls._connections[scales_socket] = (reader, writer)
                logger.log(L.SCALES, f'<{websocket_id}>⚡ Открыто новое TCP соединение с {host}:{port}')
                return reader, writer

            except Exception as e:
                exception = e
                continue

        logger.error(f'<{websocket_id}> ❌ Не удалось установить TCP соединение с {host}:{port}: {exception}')
        raise exception

    @classmethod
    async def get_or_create(cls, host: str, port: int, websocket_id: str) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Возвращает активное TCP соединение c устройством или открывает новое."""
        # Если соединение уже есть и не в состоянии закрытия, то его и возвращаем
        reader, writer = cls.get(host, port, websocket_id)

        if reader is None or writer is None:
            # Если соединения нет, то создаем новое
            reader, writer = await cls.create(host, port, websocket_id)

        return reader, writer

    @classmethod
    async def close(cls, host: str, port: int, websocket_id: str) -> None:
        """Закрываем активное соединение."""
        scales_socket = (host, port)
        if scales_socket in cls._connections:
            _, writer = cls._connections.pop(scales_socket)
            writer.close()
            await writer.wait_closed()
            logger.log(L.SCALES, f'<{websocket_id}> ⚡ Закрыто TCP соединение с устройством {host}:{port}')

    @classmethod
    async def close_all(cls) -> None:
        """Закрываем все активные соединения (например, при завершении сервера)."""
        for (host, port), (_, writer) in cls._connections.items():
            writer.close()
            await writer.wait_closed()
            logger.log(L.SCALES, f'⚡ Закрыто TCP соединение с устройством {host}:{port}')
        cls._connections.clear()


tcp_connection = TcpConnection()
