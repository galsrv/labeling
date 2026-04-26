from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings as s
from database.config import get_async_session
from core.dependencies import logging_dependency
from frontend.responses import JsonToFrontendResponse
from printers.schemas import PrinterFontSchema, PrinterImageSchema, PrinterReadSchema, PrinterCreateUpdateSchema, PrinterShortSchema
from printers.service import printers_service

api_printers_router = APIRouter()


@api_printers_router.get(
    '/',
    response_model=list[PrinterReadSchema],
    summary='Получить все принтеры'
)
async def get_all_printers(
    session: AsyncSession = Depends(get_async_session)
) -> list[PrinterReadSchema]:
    """Эндпоинт получения всех принтеров."""
    printers = await printers_service.get_all(session)
    return printers


@api_printers_router.get(
    '/{printer_id}',
    response_model=PrinterReadSchema,
    summary='Получить принтер'
)
async def get_printer(
    printer_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> PrinterReadSchema:
    """Эндпоинт получения принтера."""
    printer = await printers_service.get(session, printer_id)
    return printer


@api_printers_router.post(
    '/',
    response_model=PrinterReadSchema,
    summary='Создать принтер'
)
async def create_printer(
    data_input: PrinterCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> PrinterReadSchema:
    """Эндпоинт создания принтера."""
    response = await printers_service.create(session, data_input)
    return response


@api_printers_router.put(
    '/{printer_id}',
    response_model=PrinterReadSchema,
    summary='Изменить принтер'
)
async def update_printer(
    printer_id: int,
    data_input: PrinterCreateUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> PrinterReadSchema:
    """Эндпоинт изменения принтера."""
    response = await printers_service.update(session, printer_id, data_input)
    return response


@api_printers_router.delete(
    '/{printer_id}',
    summary='Удалить принтер'
)
async def delete_printer(
    printer_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """Эндпоинт удаления принтера."""
    await printers_service.delete(session, printer_id)


@api_printers_router.post(
        '/test_connection',
        response_model=JsonToFrontendResponse,
        name='web_printer_test_connection',
        summary='Проверка соединения с принтером',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_test_connection(
    printer_dto: PrinterShortSchema,
) -> JsonToFrontendResponse:
    """Производим тест подключения."""
    return await printers_service.test_connection(printer_dto)


@api_printers_router.post(
        '/load_font',
        response_model=JsonToFrontendResponse,
        name='web_printer_load_font',
        summary='Загрузка шрифта в принтер',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_load_font(
    font_id: int = Form(),
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
    font_file: UploadFile = File(),
) -> JsonToFrontendResponse:
    """Загружаем шрифт в принтер.

    Ограничения:
    1. В параметрах функции не смешиваем модель Pydantic и File/Form, есть риск запутать FastAPI.
    Модель Pydantic создаем внутри функции.
    2. Не передаем объект fastapi.UploadFile между слоями приложения, преобразуем в байт-строку прямо здесь
    """
    if font_file.size > s.PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES:
        return JsonToFrontendResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    font_file_bytes: bytes = await font_file.read()

    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
        font = PrinterFontSchema(font_id=font_id, file_bytes=font_file_bytes, filename=font_file.filename, content_type=font_file.content_type)

    except ValidationError as e:
        return JsonToFrontendResponse(ok=False, message=str(e))

    return await printers_service.load_font(printer, font)


@api_printers_router.post(
        '/load_image',
        response_model=JsonToFrontendResponse,
        name='web_printer_load_image',
        summary='Загрузка картинки в принтер',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_load_image(
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
    image_file: UploadFile = File(),
) -> JsonToFrontendResponse:
    """Загружаем картинку в принтер."""
    if image_file.size > s.PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES:
        return JsonToFrontendResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    image_file_bytes: bytes = await image_file.read()

    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
        image = PrinterImageSchema(file_bytes=image_file_bytes, filename=image_file.filename)

    except ValidationError as e:
        return JsonToFrontendResponse(ok=False, message=str(e))

    return await printers_service.load_image(printer, image)


@api_printers_router.post(
        '/send_arbitrary_command',
        response_model=JsonToFrontendResponse,
        response_model_exclude_none=True,
        name='web_printer_send_arbitrary_command',
        summary='Отправка произвольной команды',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_send_arbitrary_command(
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
    command: str = Form(),
) -> JsonToFrontendResponse:
    """Отправляем произвольную команду на принтер."""
    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)

    except ValidationError as e:
        return JsonToFrontendResponse(ok=False, message=str(e))

    return await printers_service.send_arbitrary_command(printer, command)
