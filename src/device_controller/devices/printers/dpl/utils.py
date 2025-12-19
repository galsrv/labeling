from validators.response import PrinterResponse


def decode_response(data: bytes) -> PrinterResponse | None:
    """Заглушка для декодирования ответа принтера."""
    if data:
        return PrinterResponse(data.decode())

    return None
