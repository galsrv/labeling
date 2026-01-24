from ipaddress import IPv4Address
from pydantic import BaseModel
import websockets

from core.config import settings as s
from core.log import logger, L


class WsMessageSchema(BaseModel):
    """Модель сообщения для отправки на устройство."""
    mode: str
    ip: IPv4Address
    port: int
    driver: str


class WsMessagePrinterSchema(WsMessageSchema):
    """Модель сообщения для отправки на принтер."""
    print_command: str


class DevicesExchange:
    """Класс методов вебсокет-клиента для обмена с утройствами."""

    async def send_print_job(self, ip: IPv4Address, port: int, driver: str, print_command: str) -> None:
        """Отправляем команду на печать на устройство."""
        async with websockets.connect(s.DEVICE_CONTROLER_URI) as ws:
            ws_message = WsMessagePrinterSchema(mode='send', ip=ip.compressed, port=port, driver=driver, print_command=print_command)
            ws_message_json = ws_message.model_dump_json()
            await ws.send(ws_message_json)
            logger.log(L.WEBSOCKETS, f'Команда на печать отправлена на {ip}:{port}')


device_exchange = DevicesExchange()
