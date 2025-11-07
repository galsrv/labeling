import asyncio

from loguru import logger
from websockets.asyncio.server import serve

from core.config import settings as s
from core.handlers import handler

async def main():
    '''Запускаем webockets-сервер.'''
    async with serve(handler, s.WS_HOST, s.WS_PORT) as server:
        logger.info(f'🚀 Websockets сервер запущен на адресе {s.WS_HOST}:{s.WS_PORT}')
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('❌ Websockets сервер остановлен вручную')