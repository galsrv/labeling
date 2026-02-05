from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates, settings as s
from core.database import get_async_session
from core.dependencies import logging_dependency
from frontend.responses import WebJsonResponse
from printers.schemas import (
    PrinterShortSchema,
    PrinterFontSchema,
    PrinterImageSchema,
)
from printers.service import web_printers_service

web_printers_router = APIRouter()


@web_printers_router.post(
        '/test_connection',
        response_model=WebJsonResponse,
        name='web_printer_test_connection',
        summary='Проверка соединения с принтером',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_test_connection(
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
) -> WebJsonResponse:
    """Производим тест подключения."""
    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
    except ValidationError as e:
        return WebJsonResponse(ok=False, message=str(e))

    return await web_printers_service.test_connection(printer)


@web_printers_router.post(
        '/load_font',
        response_model=WebJsonResponse,
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
) -> WebJsonResponse:
    """Загружаем шрифт в принтер."""
    if font_file.size > s.PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES:
        return WebJsonResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    # Не стоит передать объект fastapi.UploadFile между слоями приложения
    font_file_bytes: bytes = await font_file.read()

    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
        font = PrinterFontSchema(font_id=font_id, file_bytes=font_file_bytes, filename=font_file.filename, content_type=font_file.content_type)
    except ValidationError as e:
        return WebJsonResponse(ok=False, message=str(e))

    return await web_printers_service.load_font(printer, font)


@web_printers_router.post(
        '/load_image',
        response_model=WebJsonResponse,
        name='web_printer_load_image',
        summary='Загрузка картинки в принтер',
        dependencies=[Depends(logging_dependency)]
)
async def web_printer_load_image(
    ip: str = Form(),
    port: int = Form(),
    driver_name: str = Form(),
    image_file: UploadFile = File(),
) -> WebJsonResponse:
    """Загружаем картинку в принтер."""
    if image_file.size > s.PRINTER_MAX_FONT_IMAGE_FILE_SIZE_BYTES:
        return WebJsonResponse(ok=False, message=s.MESSAGE_WRONG_FILESIZE)

    image_file_bytes: bytes = await image_file.read()

    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
        image = PrinterImageSchema(file_bytes=image_file_bytes, filename=image_file.filename)

    except ValidationError as e:
        return WebJsonResponse(ok=False, message=str(e))

    return await web_printers_service.load_image(printer, image)


@web_printers_router.post(
        '/send_arbitrary_command',
        response_model=WebJsonResponse,
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
) -> WebJsonResponse:
    """Отправляем произвольную команду на принтер."""
    try:
        printer = PrinterShortSchema(ip=ip, port=port, driver_name=driver_name)
    except ValidationError as e:
        return WebJsonResponse(ok=False, message=str(e))

    return await web_printers_service.send_arbitrary_command(printer, command)


@web_printers_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список принтеров',
        name='web_get_all_printers',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_printers(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список принтеров."""
    all_printers = await web_printers_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='printers.html',
        context={'all_printers': all_printers}
    )


@web_printers_router.get(
        '/create',
        response_class=HTMLResponse,
        name='web_create_printer_form',
        summary='Форма создания принтера',
        dependencies=[Depends(logging_dependency)]
)
async def web_create_printer_form(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем форму создания нового принтера."""
    context = await web_printers_service.create_form(session)

    return templates.TemplateResponse(
        request=request,
        name='printer_edit.html',
        context=context
    )


@web_printers_router.post(
        '/create',
        name='web_create_printer',
        summary='Создание принтера',
        response_model=None,
        dependencies=[Depends(logging_dependency)]
)
async def web_create_printer(
    request: Request,
    ip: str = Form(),
    port: int = Form(),
    driver_id: int = Form(),
    description: str = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse | HTMLResponse:
    """Создаем принтер на основании значений полей формы."""
    printer_id: int | None = await web_printers_service.create(session, ip, port, driver_id, description)

    # При некорректно введенных данных рендерим страницу повторно и выдаем плашку из данных контекста
    if not printer_id:
        context = await web_printers_service.create_form(session)
        context['error_message'] = s.MESSAGE_SAVE_DATA_ERROR
        return templates.TemplateResponse(
            request=request,
            name='printer_edit.html',
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(
        url=request.url_for('web_update_printer_form', printer_id=printer_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_printers_router.get(
        '/{printer_id}',
        response_class=HTMLResponse,
        name='web_update_printer_form',
        summary='Форма изменения принтера',
        dependencies=[Depends(logging_dependency)]
)
async def web_update_printer_form(
    printer_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем форму изменения данных принтера."""
    context = await web_printers_service.update_form(session, printer_id)

    return templates.TemplateResponse(
        request=request,
        name='printer_edit.html',
        context=context
    )


@web_printers_router.post(
        '/{printer_id}',
        name='web_update_printer',
        summary='Изменение данных принтера',
        response_model=None,
        dependencies=[Depends(logging_dependency)]
)
async def web_update_printer(
    printer_id: int,
    request: Request,
    ip: str = Form(),
    port: int = Form(),
    driver_id: int = Form(),
    description: str = Form(),
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse | HTMLResponse:
    """Сохраняем изменения данных принтера на основании значений полей формы."""
    updated_printer_id: int | None = await web_printers_service.update(session, printer_id, ip, port, driver_id, description)

    # При некорректно введенных данных рендерим страницу повторно и выдаем плашку из данных контекста
    if not updated_printer_id:
        context = await web_printers_service.update_form(session, printer_id)
        context['error_message'] = s.MESSAGE_SAVE_DATA_ERROR
        return templates.TemplateResponse(
            request=request,
            name='printer_edit.html',
            context=context,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(
        url=request.url_for('web_update_printer_form', printer_id=printer_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@web_printers_router.post(
        '/{printer_id}/delete',
        response_class=HTMLResponse,
        name='web_delete_printer',
        summary='Удаление принтера',
        dependencies=[Depends(logging_dependency)]
)
async def web_delete_printer(
    printer_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Удаляем принтер."""
    await web_printers_service.delete(session, printer_id)

    return RedirectResponse(
        url=request.url_for('web_get_all_printers'),
        status_code=status.HTTP_303_SEE_OTHER,
    )
