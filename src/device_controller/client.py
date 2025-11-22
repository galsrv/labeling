import asyncio
import json
import sys
from typing import Callable

from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import connect

from core.log import logger
from validators.request import Commands

uri = "ws://127.0.0.1:8000"


class Client:
    """Вебсокет-клиент для теста оборудования.

    Запуск python client.py <команда> <ip_весов> <порт_весов> <драйвер>

                    << STREAM >>
        Тензо-М ТВ020           python client.py stream 192.168.90.100 33310 tenzo_m
        MettlerToledo IND226    python client.py stream 192.168.238.51 4003 mt_sics
        DIGI DI-160             python client.py stream 192.168.238.51 4004 dDIGI igi_di160
        Симулятор               python client.py stream 127.0.0.1 9999 tenzo_m

                    << GET >>
        Тензо-М ТВ020           python client.py get 192.168.90.100 33310 tenzo_m
        MettlerToledo IND226    python client.py get 192.168.238.51 4003 mt_sics
        DIGI DI-160             python client.py get 192.168.238.51 4004 digi_di160
        Симулятор               python client.py get 127.0.0.1 9999 tenzo_m

                    << STATUS >>
        Тензо-М ТВ020           python client.py status 192.168.90.100 33310 tenzo_m
        MettlerToledo IND226    python client.py status 192.168.238.51 4003 mt_sics
        DIGI DI-160             python client.py status 192.168.238.51 4004 digi_di160
        Симулятор               python client.py status 127.0.0.1 9999 tenzo_m

    """
    async def __exchange(self, host: str, port: str, driver: str, command: str, stop: bool = False, responses_to_wait: int = 1) -> None:
        """Базовый метод для отправки запросов серверу и получения ответов."""
        start_command = {'command': command, 'ip': host, 'port': port, 'driver': driver}
        stop_command = {'command': 'stop', 'ip': host, 'port': port, 'driver': driver}

        async with connect(uri) as websocket:
            try:
                start_command_json = json.dumps(start_command)
                await websocket.send(start_command_json)
                logger.info(f'➡️  Отправлена команда: {start_command}')

                responses_received = 0  # считаем содержательные ответы
                async for message in websocket:
                    responses_received += 1
                    logger.info(f'⬅️  Получен ответ: ({responses_received}) {message}')

                    message_dict: dict = json.loads(message)
                    if 'data' not in message_dict:
                        logger.error('❌  Получен неверный формат ответа. Обмен остановлен.')
                        break

                    # Получаем только необходимое число ответов
                    if responses_received >= responses_to_wait:
                        break

                # Если обмен предусматривает команду стоп...
                if stop:
                    stop_command_json = json.dumps(stop_command)
                    await websocket.send(stop_command_json)
                    logger.info(f"➡️  Отправлена команда: {stop_command}")

                    async for message in websocket:
                        logger.info(f"⬅️  Получен ответ: {message}")
                        break

            except ConnectionClosed:
                logger.info('❌ Соединение было закрыто')

    async def stream(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды STREAM."""
        await self.__exchange(host, port, driver, command='stream', stop=True, responses_to_wait=10)

    async def get(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды GET."""
        await self.__exchange(host, port, driver, command='get', stop=False, responses_to_wait=3)

    async def status(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды STATUS."""
        await self.__exchange(host, port, driver, command='status', stop=False, responses_to_wait=1)


client = Client()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("❌ Использование: python client.py <command> <ip> <port> <driver>")
        sys.exit(1)

    command, host, port, driver = sys.argv[1:5]

    if command not in Commands:
        print(f'❌ Неизвестная команда {command}')
        sys.exit(1)

    try:
        handler: Callable = getattr(client, command, None)

        if handler is None:
            print(f'❌ Класс Client не имеет метода {command}')
            sys.exit(1)

        asyncio.run(handler(host, port, driver))

    except KeyboardInterrupt:
        print('❌ Соединение было разорвано')
