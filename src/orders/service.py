import asyncio
from typing import TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from database.exceptions import ObjectNotFoundError
from frontend.responses import JsonToFrontendResponse
from labels.service import labels_service
from orders.models import OrderStatus
from orders.repository import orders_repo
from orders.schemas import OrderPageSchema, OrderReadSchema, OrderUpdateSchema
from sgtins.models import SgtinStatus
from sgtins.schema import SgtinSchema
from sgtins.service import sgtin_service
from workplaces.schemas import WorkplaceReadSchema
from workplaces.service import workplaces_service

T = TypeVar('T', bound=BaseModel)


class OrdersService:
    """Сервисный слой для производственный заданий."""
    async def get_page(self,
            session: AsyncSession,
            page: int,
            size: int,
        ) -> OrderPageSchema:
        """Возвращаем страницу списка заданий на производство."""
        items, page, pages, size, total = await orders_repo.get_page(session, page, size)

        orders_page_dto = OrderPageSchema(
            items=[OrderReadSchema.model_validate(item) for item in items],
            page=page,
            pages=pages,
            size=size,
            total=total,
        )
        return orders_page_dto

    async def get_order(self, session: AsyncSession, order_id: int) -> OrderReadSchema:
        """Возвращаем задание по его id."""
        order_orm = await orders_repo.get(session, order_id)
        order_dto = OrderReadSchema.model_validate(order_orm)
        return order_dto

    async def update_order_amounts(self, session: AsyncSession, order_id: int, produced_kg_updated: float) -> OrderReadSchema:
        """Обновляем произведенные объемы в задании на производство.

        Число коробов пока не обновляем.
        """
        order_update_dto = OrderUpdateSchema(status=OrderStatus.ACTIVE, produced_kg=produced_kg_updated)
        order_orm = await orders_repo.update(session, order_id, order_update_dto)
        order_dto = OrderReadSchema.model_validate(order_orm)
        return order_dto

    async def batch_print(self, order_id: int, number_to_print: int, workplace_id: str, session: AsyncSession) -> JsonToFrontendResponse:
        """Печатаем заданное количество этикеток."""
        # Проверяем, что передан id рабочего места, что такое рабочее место есть, что у этого рабочего места указан принтер #1
        try:
            workplace_id = int(workplace_id)
            workplace_dto: WorkplaceReadSchema = await workplaces_service.get(session, workplace_id)

            printer_dto = workplace_dto.printer1

            if printer_dto is None:
                raise ObjectNotFoundError

        except (ValueError, ObjectNotFoundError):
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_WRONG_WORKPLACE)

        # Проверяем, что введенное число этикеток не превышает установленный максимум
        if not 1 <= number_to_print <= s.BATCH_PRINT_MAX_NUMBER_OF_LABELS:
            logger.warning(s.MESSAGE_WRONG_AMOUNT_BATCH_LABEL_PRINT)
            return JsonToFrontendResponse(ok=False, message=s.MESSAGE_WRONG_AMOUNT_BATCH_LABEL_PRINT)

        order_dto: OrderReadSchema = await self.get_order(session, order_id)

        sgtins: list[SgtinSchema] = await sgtin_service.get_all_by_gtin(session, order_dto.item.gtin)

        # Проверяем, что в БД есть достаточно число кодов маркировки для печати
        if len(sgtins) < number_to_print:
            logger.warning(f'{s.MESSAGE_NOT_ENOUGH_CODES_TO_PRINT} {len(sgtins)}')
            return JsonToFrontendResponse(ok=False, message=f'{s.MESSAGE_NOT_ENOUGH_CODES_TO_PRINT} {len(sgtins)}')

        printed_sgtins_ids = list()

        try:
            # Печатаем в цикле
            for i in range(number_to_print):
                label_context = {
                    'items': order_dto.item,
                    'sgtins': sgtins[i],
                }
                response = await labels_service.print_label(session, printer_dto, order_dto.item.item_label_template.print_command, label_context)

                if not response.ok:
                    return JsonToFrontendResponse(ok=False, message=response.message or s.MESSAGE_ERROR_LABEL_PRINTING)

                printed_sgtins_ids.append(sgtins[i].id)

                await asyncio.sleep(s.BATCH_PRINT_DELAY)

        except Exception as e:
            return JsonToFrontendResponse(ok=False, message=str(e) or s.MESSAGE_ERROR_LABEL_PRINTING)

        finally:
            # Обновляем статус у напечатанных кодов маркировки
            await sgtin_service.batch_status_change(session, printed_sgtins_ids, SgtinStatus.PRINTED)
            # Обновляем ФАКТ у задания на основании числа напечатанных этикеток
            await self.update_order_amounts(session, order_dto.id, order_dto.produced_kg + order_dto.item.nominal_weight * len(printed_sgtins_ids))

        return JsonToFrontendResponse(ok=True, message=f'{s.MESSAGE_NUMBER_OF_LABELS_PRINTED} {number_to_print}')


orders_service = OrdersService()
