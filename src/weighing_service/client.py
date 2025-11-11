import asyncio
import json
import sys

from loguru import logger
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import connect

uri = "ws://127.0.0.1:8000"


async def hello(host: str, port: str) -> None:
    """Вебсокет-клиент для теста весового сервера.

    Рекомендуется запускать как python client.py <ip_весов> <порт_весов>
    Тензо-М ТВ020 python client.py 192.168.90.100 33310
    Симулятор python client.py 127.0.0.1 9999
    """
    start_command = {'command': 'start', 'ip': host, 'port': port, 'model': 'tenzo_m'}
    stop_command = {'command': 'stop', 'ip': host, 'port': port, 'model': 'tenzo_m_tv020'}

    async with connect(uri) as websocket:
        try:
            start_command_json = json.dumps(start_command)
            await websocket.send(start_command_json)
            logger.info(f"➡️  Отправлена команда: {start_command}")

            i = 1
            async for message in websocket:
                logger.info(f"⬅️  Получен ответ: ({i}) {message}")
                i += 1
                if i >= 10:
                    break

            stop_command_json = json.dumps(stop_command)
            await websocket.send(stop_command_json)
            logger.info(f"➡️  Отправлена команда: {stop_command}")

            async for message in websocket:
                logger.info(f"⬅️  Получен ответ: {message}")
                if 'gross' not in json.loads(message):
                    break

        except ConnectionClosed:
            logger.info('❌ Соединение было закрыто')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Использование: python client.py <ip> <port>")
        sys.exit(1)

    host, port = sys.argv[1:3]

    try:
        asyncio.run(hello(host, port))
    except KeyboardInterrupt:
        logger.info('❌ Соединение было разорвано')
