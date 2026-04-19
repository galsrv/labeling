from fastapi import APIRouter, WebSocket

from scales.service import scales_service

webscoket_scales_router = APIRouter()


@webscoket_scales_router.websocket(
        '/{scales_id}/ws_get_weight_stream/',
        name='websocket_get_weight_stream',
)
async def websocket_get_weight_stream(
    scales_id: int,
    websocket: WebSocket,
) -> None:
    """Получаем вес с весов в потоке для вывода в интерфейсе."""
    ip = websocket.query_params.get('ip')
    port = websocket.query_params.get('port')
    driver_name = websocket.query_params.get('driver_name')

    return await scales_service.get_weight_stream(ip, port, driver_name, websocket)
