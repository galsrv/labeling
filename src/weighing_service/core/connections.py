import asyncio

from loguru import logger

from core.config import settings as s


class ScaleConnectionsPool:
    """Синглтон-класс для работы с TCP-подключениями к весам."""
    _connections: dict[tuple[str, int], tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}

    @classmethod
    async def get(cls, host: str, port: int) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Возвращает активное TCP соединение c весами или открывает новое."""
        scales_socket = (host, port)

        # Если соединение уже есть и живо, то его и возвращаем
        if scales_socket in cls._connections:
            reader, writer = cls._connections[scales_socket]

            if not writer.is_closing():
                return reader, writer

            logger.warning(f"🔄 Соединение с {host}:{port} закрыто, пересоздаем")
            del cls._connections[scales_socket]

        # Если соединения нет, то создаем новое и возвращаем
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=s.GET_WEIGHT_TIMEOUT)

            cls._connections[scales_socket] = (reader, writer)
            logger.info(f"⚡ Открыто новое TCP соединение с {host}:{port}")
            return reader, writer

        except Exception as e:
            logger.error(f"❌ Не удалось установить TCP соединение с {host}:{port}: {e}")
            raise

    @classmethod
    async def close(cls, host: str, port: int) -> None:
        """Закрываем активное соединение."""
        scales_socket = (host, port)
        if scales_socket in cls._connections:
            _, writer = cls._connections.pop(scales_socket)
            writer.close()
            await writer.wait_closed()
            logger.info(f"🔚 Закрыто TCP соединение с весами {host}:{port}")

    @classmethod
    async def close_all(cls) -> None:
        """Закрываем все активные соединения (например, при завершении сервера)."""
        for (host, port), (_, writer) in cls._connections.items():
            writer.close()
            await writer.wait_closed()
            logger.info(f"🔚 Закрыто TCP соединение с весами {host}:{port}")
        cls._connections.clear()


scale_connections = ScaleConnectionsPool()
