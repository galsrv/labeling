from pydantic import BaseModel

from drivers.validators import ScalesResponse


class JsonToFrontendResponse(BaseModel):
    """Структура ответа фронтенду в формате JSON."""
    ok: bool
    message: str | None = None
    data: str | ScalesResponse | None = None
