import asyncio

from core.config import settings as s


async def read_until_crlf(reader: asyncio.StreamReader) -> bytes:
    r"""Читаем фрейм между двумя переводами строки '\r\n'."""
    return await reader.readuntil(b'\r\n')


async def read_fixed_length(reader: asyncio.StreamReader) -> bytes:
    """Читаем фрейм фиксированного размера."""
    return await reader.read(s.DEVICE_RESPONSE_SIZE_BYTES)
