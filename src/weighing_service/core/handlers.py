import asyncio
import json

from loguru import logger
from pydantic import ValidationError
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from core.config import settings as s
from core.validators import RequestModel, Commands
from scales.base import BaseWeightClient
from scales.drivers import get_driver

SCALE_LOCKS: dict[str, asyncio.Task] = {}
# Коннекты ко всем весам, храним задачу сервера, а также стрим
CONNECTIONS: dict[tuple[int], tuple[asyncio.Task, asyncio.StreamReader, asyncio.StreamWriter]] = {}

async def _main_loop(websocket: ServerConnection, driver: BaseWeightClient, request: RequestModel) -> None:
    '''Получаем вес с весов в режиме пуллинга и отправляем клиенту.'''
    while True:
        try:
            response: dict = await driver.get_gross_weight(request.ip.compressed, request.port)
            await _send_message(websocket, response)
            await asyncio.sleep(s.GET_WEIGHT_POLL_INTERVAL)
        except asyncio.CancelledError:
            logger.info(f'🛑 Цикл опроса весов {request.ip}:{request.port} остановлен')
            raise  # Повторно вызываем исключение чтобы задача была помечена отмененной
        except ConnectionClosed:
            logger.info('❌  Соединение закрыто')
        except Exception as e:
            logger.error(f'⚠️ Ошибка в цикле опроса весов: {e}')

async def _send_message(websocket: ServerConnection, data: dict) -> None:
    data_json: str = json.dumps(data, ensure_ascii=False)
    await websocket.send(data_json)
    logger.info(f'➡️  Отправлен ответ {data_json}')

async def handler(websocket: ServerConnection):
    """Обрабатываем запросы конкретного клиента."""
    poll_task: asyncio.Task | None = None
    scales_ip: str | None = None
    driver = None

    try:
        async for request_text in websocket:
            request = json.loads(request_text)

            # Проверяем корректность и полноту запроса
            try:
                request = RequestModel(**request)
                logger.info(f'⬅️  Получен запрос {request.command} для {request.ip}:{request.port}')
            except ValidationError:
                await _send_message(websocket, {'error': s.ERROR_REQUEST_VALIDATION})
                continue

            scales_ip = request.ip.compressed

            # Обрабатываем команду start
            if request.command == Commands.start:
                driver = get_driver(request.model)

                # Если драйвер не нашли...
                if driver is None:
                    await _send_message(websocket, {'error': s.ERROR_DRIVER_NOT_FOUND})
                    continue

                # Проверяем наличие активных подключений к этим весам, блокируем вторую попытку подключения
                if scales_ip in SCALE_LOCKS:
                    await _send_message(websocket, {'error': f'Устройство {scales_ip} уже занято'})
                    logger.warning(f'🚫 Попытка второго подключения к {scales_ip}')
                    continue

                # Создаем новую задачу опроса весов
                poll_task = asyncio.create_task(_main_loop(websocket, driver, request))
                SCALE_LOCKS[scales_ip] = poll_task
                logger.info(f'🔒  Создана новая задача на получение данных с весов {request.ip}:{request.port}')

            # Обрабатываем команду stop, может быть отправлена как исходным клиентом, так и для перехвата весов
            elif request.command == Commands.stop:
                if scales_ip in SCALE_LOCKS:
                    task = SCALE_LOCKS.pop(scales_ip)
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                    # Отдельно останавливаем соединение с весами
                    if driver: 
                        await driver.close_connection(request.ip, request.port)
                    await _send_message(websocket, {'message': s.MESSAGE_EXCHANGE_STOPPED})
                    logger.info(f'🔓 Задача на получение данных с весов {scales_ip} отменена клиентом')

    except ConnectionClosed:
        logger.info('🔌 Клиент закрыл соединение')

    finally:
        # Чистим данные в конце работы
        # Удаляем задачи в спуле сервера
        if scales_ip and scales_ip in SCALE_LOCKS:
            task = SCALE_LOCKS.pop(scales_ip)
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
            logger.info(f'🧹 Освобождено устройство {scales_ip} (клиент отключился)')
        # Удаляем соединения с весами
        if driver:
            await driver.close_all_connections()

