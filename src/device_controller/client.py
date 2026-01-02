import asyncio
import json
import sys
from typing import Callable

from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import connect

from core.log import logger
from validators.base import Modes

uri = "ws://127.0.0.1:8000"

data = (
    "<STX>yUUC<CR>"
    "<STX>L<CR>"
    "4911u6601000100P015P009Тестовый текст шрифтом Oswald: абвгдеёжзикл...уфцчщьъэюя123()_\"\"<CR>"
    "4911u7701000200P015P009Тестовый EAN13:<CR>"
    "4F00" + "070" + "01000350" + "012345678901<CR>"
    "4911u7705000200P015P009Тестовый GS1 DataMatrix:<CR>"
    "4W1c00" + "000" + "05000400" + "2000" + "000000" + "<FNC1>" + "0104603934000793215?ZjQDTZ4NBNy<GS>93zFAP<CR>"
    "4911u5501000500P015P009Тестовая картинка:<CR>"
    "1Y00" + "000" + "05000500" + "vilka<CR>"
    "E<CR>"
)


class Client:
    """Вебсокет-клиент для теста оборудования.

    Запуск python client.py <команда> <ip_устройства> <порт_устройства> <драйвер>

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

                    << SEND >>
        Datamax I4212-e         python client.py send 192.168.90.3 9100 dpl
    """
    async def __exchange(self, host: str, port: str, driver: str, mode: str, stop: bool = False, responses_to_wait: int = 1) -> None:
        """Базовый метод для отправки запросов серверу и получения ответов."""
        start_command = {'mode': mode, 'ip': host, 'port': port, 'driver': driver}
        stop_command = {'mode': 'stop', 'ip': host, 'port': port, 'driver': driver}

        if mode == 'send':
            start_command['print_command'] = data

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
        await self.__exchange(host, port, driver, mode='stream', stop=True, responses_to_wait=10)

    async def get(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды GET."""
        await self.__exchange(host, port, driver, mode='get', stop=False, responses_to_wait=3)

    async def status(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды STATUS."""
        await self.__exchange(host, port, driver, mode='status', stop=False, responses_to_wait=1)

    async def send(self, host: str, port: str, driver: str) -> None:
        """Обработчик команды SEND."""
        await self.__exchange(host, port, driver, mode='send', stop=False, responses_to_wait=1)


client = Client()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("❌ Использование: python client.py <mode> <ip> <port> <driver>")
        sys.exit(1)

    mode, host, port, driver = sys.argv[1:5]

    if mode not in Modes:
        print(f'❌ Неизвестный режим работы: {mode}')
        sys.exit(1)

    try:
        handler: Callable = getattr(client, mode, None)

        if handler is None:
            print(f'❌ Класс Client не имеет метода {mode}')
            sys.exit(1)

        asyncio.run(handler(host, port, driver))

    except KeyboardInterrupt:
        print('❌ Соединение было разорвано')
