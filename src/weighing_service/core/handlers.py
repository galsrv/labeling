import asyncio
import json

from loguru import logger
from pydantic import ValidationError
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from core.connections import scale_connections
from core.config import settings as s
from core.validators import ServerRequest, ScalesResponse, ServerResponse, Commands, ResponseTypes
from scales.base import BaseWeightClient
from scales.drivers import get_driver

ACTIVE_WEBSOCKETS: dict[tuple[str, int], asyncio.Task] = {}


async def __send_message(websocket: ServerConnection, response: ServerResponse) -> None:
    """Форматируем ответ по шаблону и отправляем клиенту."""
    data_json = response.model_dump_json(ensure_ascii=False)

    await websocket.send(data_json)
    logger.info(f'➡️  Отправлен ответ {data_json}')


async def __main_loop(websocket: ServerConnection, driver: BaseWeightClient, request: ServerRequest) -> None:
    """Получаем вес с весов в режиме пуллинга и отправляем клиенту."""
    while True:
        try:
            scales_response: ScalesResponse = await driver.get_gross_weight(request.ip.compressed, request.port)
            server_response = ServerResponse.model_validate(scales_response)
            await __send_message(websocket, server_response)
            await asyncio.sleep(s.GET_WEIGHT_POLL_INTERVAL)
        except ConnectionClosed:
            logger.info('❌  Соединение закрыто')
        except Exception as e:
            logger.error(f'⚠️ Ошибка в цикле опроса весов: {e}')


async def __start_command_handler(websocket: ServerConnection, request: ServerRequest, scales_socket: tuple[str, int]) -> None:
    """Обрабатываем команду START."""
    driver = get_driver(request.model)

    # Если драйвер не нашли...
    if driver is None:
        response = ServerResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_DRIVER_NOT_FOUND)
        await __send_message(websocket, response)
        return

    # Проверяем наличие активных подключений к этим весам, блокируем вторую попытку подключения
    if scales_socket in ACTIVE_WEBSOCKETS:
        response = ServerResponse(ok=False, type=ResponseTypes.error, data=None, message=f'Устройство {scales_socket} уже занято')
        await __send_message(websocket, response)
        logger.warning(f'🚫 Попытка второго подключения к {scales_socket}')
        return

    # Создаем новую задачу опроса весов
    poll_task = asyncio.create_task(__main_loop(websocket, driver, request))
    ACTIVE_WEBSOCKETS[scales_socket] = poll_task
    logger.info(f'🔒  Создана новая задача на получение данных с весов {scales_socket}')


async def __stop_command_handler(websocket: ServerConnection, request: ServerRequest, scales_socket: tuple[str, int]) -> None:
    """Обрабатываем команду STOP."""
    if scales_socket in ACTIVE_WEBSOCKETS:
        # Удаляем задачу в спуле сервера
        task = ACTIVE_WEBSOCKETS.pop(scales_socket)
        task.cancel()  # вызывает asyncio.CancelledError в момент, когда __main_loop натыкается на await
        await asyncio.gather(task, return_exceptions=True)  # для корректного закрытия задачи

        # Отдельно закрываем TCP-соединение с весами
        await scale_connections.close(*scales_socket)
        response = ServerResponse(ok=True, type=ResponseTypes.info, data=None, message=s.MESSAGE_EXCHANGE_STOPPED)
        await __send_message(websocket, response)
        logger.info(f'🔓 Задача на получение данных с весов {scales_socket} отменена клиентом')


async def handler(websocket: ServerConnection) -> None:
    """Основной хендлер запросов."""
    scales_socket: tuple[str, int] | None = None

    try:
        async for request_text in websocket:
            request = json.loads(request_text)

            # Проверяем корректность и полноту запроса
            try:
                request = ServerRequest(**request)
                logger.info(f'⬅️  Получен запрос {request.command} для {request.ip}:{request.port}')
            except ValidationError:
                response = ServerResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_REQUEST_VALIDATION)
                await __send_message(websocket, response)
                continue

            scales_socket = (request.ip.compressed, request.port)

            # Обрабатываем команду start
            if request.command == Commands.start:
                await __start_command_handler(websocket, request, scales_socket)

            # Обрабатываем команду stop (от изначального клиента или от постороннего)
            elif request.command == Commands.stop:
                await __stop_command_handler(websocket, request, scales_socket)

            # Обрабатываем прочие команды - возвращаем ошибку
            else:
                response = ServerResponse(ok=False, type=ResponseTypes.error, data=None, message=s.ERROR_UNKNOWN_COMMNAD)
                await __send_message(websocket, response)

    except ConnectionClosed:
        logger.info('🔌 Клиент закрыл соединение')

    finally:
        # Чистим данные в конце работы
        if scales_socket:
            # Удаляем задачи в спуле сервера
            if scales_socket in ACTIVE_WEBSOCKETS:
                task = ACTIVE_WEBSOCKETS.pop(scales_socket)
                if not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                logger.info(f'🧹 Освобождено устройство {scales_socket} (клиент отключился)')

            # Отдельно закрываем TCP-соединение с весами
            await scale_connections.close(*scales_socket)
