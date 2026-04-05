from datetime import datetime

from pydantic import BaseModel, ConfigDict

from sgtins.models import SgtinStatus


class SgtinCreateSchema(BaseModel):
    """Модель создания кода маркировки."""
    gtin: str
    sgtin: str
    crypto_end: str

    model_config = ConfigDict(from_attributes=True)


class SgtinUpdateSchema(BaseModel):
    """Модель изменения кода маркировки."""
    status: SgtinStatus | None = None
    printed_at: datetime | None = None
    expired_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SgtinSchema(BaseModel):
    """Модель полей кода маркировки."""
    id: int
    gtin: str
    sgtin: str
    crypto_end: str

    model_config = ConfigDict(from_attributes=True)
