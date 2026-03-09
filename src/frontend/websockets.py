from fastapi import WebSocket

from core.log import L, logger


class ConnectionManager:
    """Менеджер websocket-соединений между бэкендом и фронтендом."""
    def __init__(self) -> None:
        """Инициализатор класса."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Открываем соединение, записываем в пул соединений."""
        if websocket in self.active_connections:
            return

        await websocket.accept()
        self.active_connections.append(websocket)
        logger.log(L.WS, f'⚡ Открыт вебсокет с {websocket.client.host}:{websocket.client.port}')

    async def close(self, websocket: WebSocket, code: int = 1000, reason: str | None = None) -> None:
        """Закрываем соединение."""
        try:
            await websocket.close(code=code, reason=reason)
        except RuntimeError:
            # Вебсокет уже закрыт или в некорректном состоянии
            pass

    async def disconnect(self, websocket: WebSocket, code: int = 1000, reason: str | None = None) -> None:
        """Удаляем соединение из пула."""
        await self.close(websocket, code=code, reason=reason)
        logger.log(L.WS, f'⚡ Закрыт вебсокет с {websocket.client.host}:{websocket.client.port}')

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket) -> None:
        """Отправляем сообщение фронтенду."""
        await websocket.send_text(message)
        logger.log(L.WS, f'⚡ Отправлено сообщение {message} адресу {websocket.client.host}:{websocket.client.port}')


ws_connection_manager = ConnectionManager()
