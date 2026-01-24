from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import templates
from core.database import get_async_session
from core.dependencies import logging_dependency
from workplaces.service import web_scales_service, web_printers_service, web_workplaces_service

web_scales_router = APIRouter()

web_printers_router = APIRouter()

web_workplaces_router = APIRouter()


@web_scales_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список весов',
        name='web_get_all_scales',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_scales(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список весов."""
    all_scales = await web_scales_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='scales.html',
        context={'all_scales': all_scales}
    )


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


@web_workplaces_router.get(
        '/',
        response_class=HTMLResponse,
        summary='Список рабочих мест',
        name='web_get_all_workplaces',
        dependencies=[Depends(logging_dependency)]
)
async def web_get_all_workplaces(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> HTMLResponse:
    """Отображаем список рабочих мест."""
    all_workplaces = await web_workplaces_service.get_all(session)
    return templates.TemplateResponse(
        request=request,
        name='workplaces.html',
        context={'all_workplaces': all_workplaces}
    )
