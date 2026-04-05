import asyncio
from typing import TypeVar
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from core.exceptions import ObjectNotFound
from frontend.responses import WebJsonResponse
from labels.service import labels_service
from printers.schemas import PrinterReadWebSchema
from printers.service import printers_service
from sgtins.models import SgtinStatus
from sgtins.schema import SgtinSchema
from sgtins.service import sgtin_service
from orders.models import OrderStatus
from orders.repository import orders_repo
from orders.schemas import OrderReadSchema, OrderWebSchema, OrderUpdateSchema

T = TypeVar('T', bound=BaseModel)


class OrdersService:
    """Сервисный слой для производственный заданий."""
    def __init__(self, read_model: type[BaseModel]) -> None:
        """Инициализация объекта класса."""
        self.read_model = read_model

    async def list_orders(self, session: AsyncSession) -> list[T]:
        """Возвращаем из БД все задания."""
        orders = await orders_repo.get_all(session)
        orders_dto = [self.read_model.model_validate(order) for order in orders]
        return orders_dto

    async def get_order(self, session: AsyncSession, order_id: int) -> T:
        """Возвращаем из БД задание по его id."""
        order = await orders_repo.get(session, order_id)

        if order is None:
            raise ObjectNotFound(s.MESSAGE_ENTRY_DOESNT_EXIST)

        order_dto = self.read_model.model_validate(order)
        return order_dto

    async def update_order_amounts(self, session: AsyncSession, order_id: int, produced_kg_updated: float) -> int:
        """Обновляем произведенные объемы в задании на производство.

        Число коробов пока не обновляем.
        """
        order_update_dto = OrderUpdateSchema(status=OrderStatus.ACTIVE, produced_kg=produced_kg_updated)

        order_id = await orders_repo.update(session, order_id, order_update_dto)
        return order_id

    async def batch_print(self, order_id: int, number_to_print: int, session: AsyncSession) -> WebJsonResponse:
        """Печатаем заданное количество этикеток.

        1. Проверяем, что введенное число этикеток не превышает установленный максимум.
        2. Проверяем, что в БД есть достаточно число кодов маркировки для печати.
        3. Печатаем в цикле.
        4. Обновляем статус у напечатанных кодов маркировки.
        5. Обновляем ФАКТ у задания на основании числа напечатанных этикеток.
        """
        if not 1 <= number_to_print <= s.BATCH_PRINT_MAX_NUMBER_OF_LABELS:
            logger.warning(s.MESSAGE_WRONG_AMOUNT_BATCH_LABEL_PRINT)
            return WebJsonResponse(ok=False, message=s.MESSAGE_WRONG_AMOUNT_BATCH_LABEL_PRINT)

        order_dto: OrderWebSchema = await self.get_order(session, order_id)

        sgtins: list[SgtinSchema] = await sgtin_service.get_all_by_gtin(session, order_dto.item.gtin)

        if len(sgtins) < number_to_print:
            logger.warning(f'{s.MESSAGE_NOT_ENOUGH_CODES_TO_PRINT} {len(sgtins)}')
            return WebJsonResponse(ok=False, message=f'{s.MESSAGE_NOT_ENOUGH_CODES_TO_PRINT} {len(sgtins)}')

        # Разработать функционал рабочих мест и привязку задания к текущему РМ.
        printer_dto: PrinterReadWebSchema = await printers_service.get(session, 1)

        printed_sgtins_ids = list()

        try:
            for i in range(number_to_print):
                label_context = {
                    'items': order_dto.item,
                    'sgtins': sgtins[i],
                }
                response = await labels_service.print_label(session, printer_dto, order_dto.item.item_label_template.print_command, label_context)

                if not response.ok:
                    return WebJsonResponse(ok=False, message=response.message or s.MESSAGE_ERROR_LABEL_PRINTING)

                printed_sgtins_ids.append(sgtins[i].id)

                await asyncio.sleep(s.BATCH_PRINT_DELAY)

        except Exception as e:
            return WebJsonResponse(ok=False, message=str(e) or s.MESSAGE_ERROR_LABEL_PRINTING)

        finally:
            await sgtin_service.batch_status_change(session, printed_sgtins_ids, SgtinStatus.PRINTED)
            await self.update_order_amounts(session, order_dto.id, order_dto.item.nominal_weight * len(printed_sgtins_ids))

        return WebJsonResponse(ok=True, message=f'{s.MESSAGE_NUMBER_OF_LABELS_PRINTED} {number_to_print}')


api_orders_service = OrdersService(read_model=OrderReadSchema)

web_orders_service = OrdersService(read_model=OrderWebSchema)
