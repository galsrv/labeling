import asyncio
import json

from websockets.exceptions import ConnectionClosedError
from websockets.asyncio.client import connect

IP = '192.168.90.100'
PORT = 33310 

uri = "ws://127.0.0.1:8000"

async def hello():
    
    async with connect(uri) as websocket:
        command = {'command': 'start', 'ip': IP, 'port': PORT, 'model': 'tenzo_m_tv020'}
        command = json.dumps(command)

        try:
            await websocket.send(command)
            print(f">>> {command}")
        except ConnectionClosedError:
            pass

        i = 1
        async for message in websocket:
            print(f"➡️ {i} {message}")
            i += 1
            if i >= 10:
                break

        command = {'command': 'stop', 'ip': IP, 'port': PORT, 'model': 'tenzo_m_tv020'}
        await websocket.send(json.dumps(command))
        print(f">>> {command}")

        async for message in websocket:
            print(f"➡️ {message}")
            if json.loads(message)['message'] == 'stop':
                break

if __name__ == "__main__":
    asyncio.run(hello())