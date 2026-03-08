import asyncio
from typing import TypeVar

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound

from device_drivers.drivers import scales_drivers
from device_drivers.validators import DeviceResponse, ResponseTypes

from frontend.websockets import ws_connection_manager
from frontend.responses import WebJsonResponse

from scales.repository import scales_repo
from scales.schemas import (
    ScalesShortSchema,
    ScalesReadWebSchema,
    ScalesCreateUpdateWebSchema,
)

T = TypeVar('T', bound=BaseModel)


class ScalesService:
    """Сервисный слой для весов."""

    async def __get_common_context(self) -> dict:
        """Получаем общие элементы контекста."""
        return {
            'drivers': scales_drivers.keys(),
        }

    async def get_all(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все весы."""
        scales = await scales_repo.get_all(session)
        scales_dto = [ScalesReadWebSchema.model_validate(scales) for scales in scales]
        return scales_dto

    async def get(self, session: AsyncSession, scales_id: int) -> T:
        """Возвращаем из БД весы по их id."""
        scales = await scales_repo.get(session, scales_id)

        if scales is None:
            raise ObjectNotFound(s.ERROR_MESSAGE_ENTRY_DOESNT_EXIST)

        scales_dto = ScalesReadWebSchema.model_validate(scales)
        return scales_dto

    async def update_form(self, session: AsyncSession, scales_id: int) -> dict:
        """Формируем контекст формы изменения весов."""
        context: dict = await self.__get_common_context()
        scales_dto: ScalesReadWebSchema = await self.get(session, scales_id)

        context.update({
            'mode': 'update',
            'scales': scales_dto,
        })

        return context

    async def create_form(self, session: AsyncSession) -> dict:
        """Формируем контекст формы создания весов."""
        context: dict = await self.__get_common_context()

        context.update({
            'mode': 'create',
            'scales': None,
        })

        return context

    async def create(self, session: AsyncSession, ip: str, port: int, driver_name: str, description: str) -> int | None:
        """Создаем весы, возвращаем их id."""
        try:
            scales_dto = ScalesCreateUpdateWebSchema(
                ip=ip,
                port=port,
                driver_name=driver_name,
                description=description)
        except ValidationError as e:
            from core.log import logger
            logger.debug(str(e))
            return None

        scales_id: int | None = await scales_repo.create(session, scales_dto)

        return scales_id

    async def update(self, session: AsyncSession, scales_id: int, ip: str, port: int, driver_name: str, description: str) -> None:
        """Изменяем данные весов, ничего не возвращаем."""
        try:
            scales_dto = ScalesCreateUpdateWebSchema(
                ip=ip,
                port=port,
                driver_name=driver_name,
                description=description)
        except ValidationError:
            return None

        scales_id: int | None = await scales_repo.update(session, scales_id, scales_dto)

        return scales_id

    async def delete(self, session: AsyncSession, scales_id: int) -> None:
        """Удаляем весы, ничего не возвращаем."""
        await scales_repo.delete(session, scales_id)

    async def get_weight(self, ip: str, port: int, driver_name: str) -> WebJsonResponse:
        """Получаем вес с весов."""
        try:
            scales = ScalesShortSchema(ip=ip, port=port, driver_name=driver_name)
        except ValidationError as e:
            return WebJsonResponse(ok=False, message=str(e))

        response: DeviceResponse = await scales.driver.get_weight(scales.ip.compressed, scales.port)

        return WebJsonResponse(ok=response.ok, data=response.data)

    async def get_weight_stream(self, ip: str, port: int, driver_name: str, websocket: WebSocket) -> None:
        """Получаем вес с весов в потоке."""
        await ws_connection_manager.connect(websocket)

        try:
            scales = ScalesShortSchema(ip=ip, port=port, driver_name=driver_name)
            await self._get_weight_stream_cycle(scales, websocket)

        except (ValidationError, Exception) as e:
            response = DeviceResponse(ok=False, type=ResponseTypes.error, message=str(e))
            await ws_connection_manager.send_message(response.model_dump_json(exclude_none=True), websocket)
            await ws_connection_manager.disconnect(websocket)

    async def _get_weight_stream_cycle(self, scales: ScalesShortSchema, websocket: WebSocket) -> None:
        while True:
            response: DeviceResponse = await self._get_weight_stream_iteration(scales)
            try:
                await ws_connection_manager.send_message(response.model_dump_json(exclude_none=True), websocket)
            except (WebSocketDisconnect, Exception):
                break
            await asyncio.sleep(s.DEVICE_POLL_INTERVAL)

        await ws_connection_manager.disconnect(websocket)

    async def _get_weight_stream_iteration(self, scales: ScalesShortSchema) -> DeviceResponse:
        response: DeviceResponse = await scales.driver.get_weight(scales.ip.compressed, scales.port)
        return response


scales_service = ScalesService()
