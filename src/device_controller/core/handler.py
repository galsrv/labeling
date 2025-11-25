import asyncio
import json

from pydantic import ValidationError
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from core.config import settings as s
from core.log import logger
from validators.request import ClientRequest
from validators.response import ScalesResponse, ServerResponse, ResponseTypes

ACTIVE_WEBSOCKETS: dict[tuple[str, int], asyncio.Task] = {}


class WebsocketsHandler:
    """Обработчик запросов.

    Имя метода соответствует имени команды
    """
    async def __call__(self, websocket: ServerConnection) -> None:
        """Вход в процесс обработки запросов.

        websockets.asyncio.server.serve ожидает на вход callable-объект.
        """
        await self.main_handler(websocket)

    async def dispatch(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Распределяем запросы по методам."""
        handler = getattr(self, request.command.value.lower(), self.command_not_found)
        return await handler(websocket, request)

    async def command_not_found(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Реагируем на неверную команду."""
        await self.send_message(websocket, ServerResponse(device=request.device_socket, ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_UNKNOWN_COMMNAD))

    async def send_message(self, websocket: ServerConnection, response: ServerResponse) -> None:
        """Форматируем ответ по шаблону и отправляем клиенту."""
        data_json = response.model_dump_json(ensure_ascii=False)

        try:
            await websocket.send(data_json)
            logger.info(f'<{websocket.id}> ➡️  Отправлен ответ в {websocket.remote_address}: {data_json}')
        except ConnectionClosed:
            logger.info(f'<{websocket.id}> ❌  Отправка сообщения невозможна, клиент недоступен')
            raise

    async def validate_request(self, websocket: ServerConnection, request_binary: bytes) -> ClientRequest | None:
        """Проверяем корректность и полноту запроса."""
        request_dict: dict = json.loads(request_binary)
        try:
            request = ClientRequest(**request_dict)
            logger.info(f'<{websocket.id}> ⬅️  Получен запрос {request.command} для устройства {request.device_socket}')
            return request
        except ValidationError:
            await self.send_message(websocket, ServerResponse(device=(request_dict['ip'], request_dict['port']), ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_REQUEST_VALIDATION))

    async def is_device_available(self, websocket: ServerConnection, request: ClientRequest) -> bool:
        """Проверяем наличие активных подключений к этому устройству, блокируем вторую попытку подключения."""
        return request.device_socket not in ACTIVE_WEBSOCKETS

    async def exchange_loop(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Запускаем цикл обмена с устройством + отправки данных клиенту."""
        while True:
            try:
                await self.exchange_iteration(websocket, request)
            except ConnectionClosed:
                logger.info(f'<{websocket.id}> ❌  Вебсокет закрыт, цикл остановлен')
                break

        await self.task_cancellation(websocket, request)

    async def exchange_iteration(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Осуществляем однократный обмен запрос-ответ с устройством."""
        scales_response: ScalesResponse = await request.driver.run_exchange(request.ip.compressed, request.port, websocket.id)
        server_response = ServerResponse.model_validate(scales_response)
        await self.send_message(websocket, server_response)
        await asyncio.sleep(s.GET_WEIGHT_POLL_INTERVAL)

    async def stream(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Обрабатываем команду STREAM."""
        if not await self.is_device_available(websocket, request):
            return

        # Создаем новую задачу обмена с устройством
        await self.task_creation(websocket, request)
        await self.send_message(websocket, ServerResponse(device=request.device_socket, ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_EXCHANGE_STARTED))

    async def get(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Обрабатываем команду GET."""
        if not await self.is_device_available(websocket, request):
            return

        # Однократно опрашиваем устройство
        logger.info(f'<{websocket.id}> ✅  Однократный опрос устройства {request.device_socket}')
        await self.send_message(websocket, ServerResponse(device=request.device_socket, ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_EXCHANGE_STARTED))

        await self.exchange_iteration(websocket, request)

        await self.stop_exchange(websocket, request)
        logger.info(f'<{websocket.id}> ❌  Вебсокет закрыт')
        await websocket.close()

    async def stop(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Обрабатываем команду STOP."""
        await self.task_cancellation(websocket, request)

    async def status(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Обрабатываем команду STATUS."""
        device_available = self.is_device_available(websocket, request)
        message = s.MESSAGE_DEVICE_AVAILABLE if device_available else s.MESSAGE_DEVICE_BUSY
        await self.send_message(websocket, ServerResponse(device=request.device_socket, ok=device_available, type=ResponseTypes.status, data=None, message=message))
        logger.info(f'<{websocket.id}> ✅  Проверка статуса устройства {request.device_socket}, устройство доступно = {device_available}')

    async def task_creation(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Создаем задачу на потоковое чтение данных с устройства."""
        task_name = f'Task-for-{request.ip.compressed}:{request.port}'
        poll_task = asyncio.create_task(self.exchange_loop(websocket, request), name=task_name)
        ACTIVE_WEBSOCKETS[request.device_socket] = poll_task
        logger.info(f'<{websocket.id}> ✅  Создана задача {task_name}')

    async def task_cancellation(self, websocket: ServerConnection, request: ClientRequest | None = None) -> None:
        """Отменяем задачу на потоковое чтение данных с устройства."""
        if request and request.device_socket and request.device_socket in ACTIVE_WEBSOCKETS:
            # Удаляем задачу из пула сервера
            task = ACTIVE_WEBSOCKETS.pop(request.device_socket)
            task.cancel()

            if task is not asyncio.current_task():  # Попытка отменить саму себя закончится плохо
                await asyncio.gather(task, return_exceptions=True)  # Ожидаем закрытия задачи

            logger.info(f'<{websocket.id}> ❌  Отменена задача {task.get_name()}')
            await self.stop_exchange(websocket, request)

    async def stop_exchange(self, websocket: ServerConnection, request: ClientRequest) -> None:
        """Закрываем TCP-соединение с устройством."""
        await request.driver.stop_exchange(*request.device_socket, websocket.id)
        await self.send_message(websocket, ServerResponse(device=request.device_socket, ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_EXCHANGE_STOPPED))

    async def main_handler(self, websocket: ServerConnection) -> None:
        """Точка входа в процесс обработки запросов."""
        request: ClientRequest | None = None
        logger.info(f'<{websocket.id}> ✅  Создан вебсокет с клиентом {websocket.remote_address}')

        try:
            async for request_binary in websocket:
                # Проверяем корректность и полноту запроса
                request: ClientRequest | None = await self.validate_request(websocket, request_binary)

                if request:
                    # Запускаем диспетчер и ищем подходящий метод выполнения запроса
                    await self.dispatch(websocket, request)

        except ConnectionClosed:
            logger.info(f'<{websocket.id}> ❌ Клиент закрыл соединение')
        finally:
            # Чистим данные после закрытия вебсокета
            await self.task_cancellation(request.device_socket if request else None)


handler = WebsocketsHandler()
