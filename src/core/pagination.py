from pydantic import BaseModel, ConfigDict


class BasePageSchema(BaseModel):
    """Базовый класс пагинации."""
    page: int
    pages: int
    size: int
    total: int

    model_config = ConfigDict(from_attributes=True)
