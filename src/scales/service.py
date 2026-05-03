from typing import TypeVar

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from drivers.drivers import scales_drivers
from drivers.scales.scales_base import BaseScalesDriver
from drivers.validators import DeviceResponse, ResponseTypes
from frontend.responses import JsonToFrontendResponse
from frontend.websockets import ws_connection_manager
from scales.repository import scales_repo
from scales.schemas import (
    ScalesCreateUpdateSchema,
    ScalesPageSchema,
    ScalesReadSchema,
    ScalesShortSchema,
)

T = TypeVar('T', bound=BaseModel)


class ScalesService:
    """Сервисный слой для весов."""

    async def get_page(
            self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> ScalesPageSchema:
        """Возвращаем страницу списка весов."""
        items, page, pages, size, total = await scales_repo.get_page(session, page, size)

        scales_page_dto = ScalesPageSchema(
            items=[ScalesReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return scales_page_dto

    async def get(self, session: AsyncSession, scales_id: int) -> T:
        """Возвращаем весы по их id."""
        scales = await scales_repo.get(session, scales_id)
        scales_dto = ScalesReadSchema.model_validate(scales)
        return scales_dto

    async def create(self, session: AsyncSession, scales_dto: ScalesCreateUpdateSchema) -> ScalesReadSchema:
        """Создаем весы, возвращаем их."""
        scales_orm = await scales_repo.create(session, scales_dto)
        return ScalesReadSchema.model_validate(scales_orm)

    async def update(self, session: AsyncSession, scales_id: int, scales_dto: ScalesCreateUpdateSchema) -> ScalesReadSchema:
        """Изменяем весы, возвращаем их."""
        scales_orm = await scales_repo.update(session, scales_id, scales_dto)
        return ScalesReadSchema.model_validate(scales_orm)

    async def delete(self, session: AsyncSession, scales_id: int) -> None:
        """Удаляем весы, ничего не возвращаем."""
        await scales_repo.delete(session, scales_id)

    async def get_weight(self, scales_dto: ScalesShortSchema) -> JsonToFrontendResponse:
        """Получаем вес с весов однократно."""
        driver: BaseScalesDriver = scales_drivers.get(scales_dto.driver_name)
        response: DeviceResponse = await driver.get_weight(scales_dto.ip.compressed, scales_dto.port)
        return JsonToFrontendResponse(ok=response.ok, data=response.data)

    async def get_weight_stream(self, ip: str, port: int, driver_name: str, websocket: WebSocket) -> None:
        """Получаем вес с весов в потоке. Используем объект-генератор."""
        await ws_connection_manager.connect(websocket)

        try:
            scales_dto = ScalesShortSchema(ip=ip, port=port, driver_name=driver_name)
            driver: BaseScalesDriver = scales_drivers.get(scales_dto.driver_name)

            if driver is None:
                raise Exception(s.MESSAGE_WRONG_DRIVER_NAME)

            async for response in driver.get_weight_stream(ip, port):
                await ws_connection_manager.send_message(response.model_dump_json(exclude_none=True), websocket)

        except (ValidationError, WebSocketDisconnect, Exception) as e:
            response = DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))
            if not isinstance(e, WebSocketDisconnect):
                await ws_connection_manager.send_message(response.model_dump_json(exclude_none=True), websocket)

        finally:
            await ws_connection_manager.disconnect(websocket)


scales_service = ScalesService()
