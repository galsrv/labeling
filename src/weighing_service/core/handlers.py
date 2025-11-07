import asyncio
import json

from loguru import logger
from pydantic import ValidationError
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from core.config import settings as s
from core.validators import RequestModel, Commands
from scales.base import BaseWeightClient
from scales.models import get_driver

TASKS: dict[str, asyncio.Task] = {}

async def _main_loop(websocket: ServerConnection, driver: BaseWeightClient, request: RequestModel) -> None:
    '''Получаем вес с весов и отправляем клиенту, в цикле'''
    try:
        while True:
            response: dict = await driver.get_gross_weight(request.ip.compressed, request.port)
            await _send_message(websocket, response)
            await asyncio.sleep(1)
    except ConnectionClosed:
        logger.info('❌  Соединение закрыто')

async def _send_message(websocket: ServerConnection, data: dict) -> None:
    data_json: str = json.dumps(data, ensure_ascii=False)
    await websocket.send(data_json)
    logger.info(f'➡️  Отправлен ответ {data_json}')

async def handler(websocket: ServerConnection):
    '''Обрабатываем поступивший запрос.'''
    async for request in websocket:
        request = json.loads(request)

        # Проверяем корректность и полноту запроса
        try:
            request = RequestModel(**request)
            logger.info(f'⬅️  Получен запрос {request.command} для {request.ip}:{request.port}')
        except ValidationError:
            await _send_message(websocket, {'error': s.ERROR_REQUEST_VALIDATION})
            return

        # Обрабатываем команду start
        if request.command == Commands.start:
            # Ищем драйвер по указанной модели весов
            driver = get_driver(request.model)

            # Если драйвер не нашли...
            if driver is None:
                await _send_message(websocket, {'error': s.ERROR_DRIVER_NOT_FOUND})
                return

            if request.ip.compressed in TASKS.keys():
                TASKS[request.ip.compressed].cancel()
                await _send_message(websocket, {'error': s.MESSAGE_EXCHANGE_STOPPED})
                logger.info('❌  Хендлер остановлен по команде клиента')

            task: asyncio.Task = asyncio.create_task(_main_loop(websocket, driver, request))
            TASKS[request.ip.compressed] = task
            logger.info(f'🗂  Создана новая задача на получение данных с адреса {request.ip.compressed}')

        # Обрабатываем команду stop
        if request.command == Commands.stop:
            if request.ip.compressed in TASKS.keys():
                await _send_message(websocket, {'message': s.MESSAGE_EXCHANGE_STOPPED})
                TASKS[request.ip.compressed].cancel()
                logger.info('❌  Хендлер остановлен по команде клиента')


    

