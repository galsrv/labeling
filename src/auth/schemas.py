from datetime import datetime

from pydantic import BaseModel, ConfigDict

from users.schemas import UserReadSchema


class LoginRequestSchema(BaseModel):
    """Модель логина пользователя."""
    username: str
    password: str


class TokenPairSchema(BaseModel):
    """Модель токена аутентификации."""
    access_token: str
    refresh_token: str


class RefreshTokenReadSchema(BaseModel):
    """Модель создания refresh-токена аутентификации для бД."""
    id: int
    refresh_token_hash: str
    expires_at: datetime
    user: UserReadSchema

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenCreateSchema(BaseModel):
    """Модель создания refresh-токена аутентификации для бД."""
    user_id: int
    refresh_token_hash: str
    expires_at: datetime


class RefreshRequestSchema(BaseModel):
    """Модель обновления рефреш-токена."""
    refresh_token: str
