from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleReadSchema(BaseModel):
    """Модель представления роли."""
    id: int
    name: str

    is_items_view_permitted: bool
    is_items_edit_permitted: bool
    is_labels_view_permitted: bool
    is_labels_edit_permitted: bool
    is_orders_view_permitted: bool
    is_orders_edit_permitted: bool
    is_printers_view_permitted: bool
    is_printers_edit_permitted: bool
    is_scales_view_permitted: bool
    is_scales_edit_permitted: bool
    is_sgtins_view_permitted: bool
    is_sgtins_edit_permitted: bool
    is_users_view_permitted: bool
    is_users_edit_permitted: bool
    is_workplaces_view_permitted: bool
    is_workplaces_edit_permitted: bool

    model_config = ConfigDict(from_attributes=True)


class RoleCreateSchema(BaseModel):
    """Не используется."""


class RoleUpdateSchema(BaseModel):
    """Не используется."""


class UserShortSchema(BaseModel):
    """Модель сокращенного представления пользователя."""
    id: int
    username: str
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(BaseModel):
    """Модель представления пользователя."""
    id: int
    username: str
    first_name: str
    last_name: str
    is_active: bool

    created_at: datetime
    updated_at: datetime

    role: RoleReadSchema
    created_by: UserShortSchema | None = None
    updated_by: UserShortSchema | None = None

    model_config = ConfigDict(from_attributes=True)


class BaseUserCreateSchema(BaseModel):
    """Модель создания пользователя."""
    username: str
    first_name: str
    last_name: str
    is_active: bool = True
    role_id: int
    # Убрать после реализации аутентификации
    created_by_id: int
    updated_by_id: int


class BaseUserUpdateSchema(BaseModel):
    """Модель изменения пользователя."""
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    role_id: int | None = None
    updated_by_id: int


class UserCreateSchema(BaseUserCreateSchema):
    """Модель создания пользователя, включающая пароль в исходном виде."""
    password: str


class UserUpdateSchema(BaseUserUpdateSchema):
    """Модель изменения пользователя, включающая пароль в исходном виде."""
    password: str | None = None


class UserWithHashReadSchema(UserReadSchema):
    """Модель представления пользователя, включающая хэша пароля."""
    password_hash: str


class UserWithHashCreateSchema(BaseUserCreateSchema):
    """Модель создания пользователя, включающая хэша пароля."""
    password_hash: str


class UserWithHashUpdateSchema(BaseUserUpdateSchema):
    """Модель изменения пользователя, включающая хэша пароля."""
    password_hash: str | None = None
