from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from database.config import AppBaseClass


class RolesOrm(AppBaseClass):
    """Модель ролей."""
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(s.USER_ROLE_NAME_MAX_LENGTH), nullable=False)

    is_items_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_items_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_labels_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_labels_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_orders_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_orders_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_printers_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_printers_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_scales_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_scales_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_sgtins_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_sgtins_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_users_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_users_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_workplaces_view_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))
    is_workplaces_edit_permitted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))

    __table_args__ = (
        UniqueConstraint('name', name='unique_role_name'),
    )

    __order_by__ = (id, )


class UsersOrm(AppBaseClass):
    """Модель пользователей."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(s.USER_USERNAME_MAX_LENGTH), nullable=False)
    first_name: Mapped[str] = mapped_column(String(s.USER_FIRST_NAME_MAX_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(s.USER_LAST_NAME_MAX_LENGTH), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(s.USER_PASSWORD_MAX_LENGTH), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text('true'))
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey(RolesOrm.id, ondelete='RESTRICT'), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    role: Mapped[RolesOrm] = relationship(RolesOrm, lazy='joined')

    created_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[created_by_id],
        lazy='joined',
        # Если не ограничить глубину, можно запустить бескочненый цикл жадной загрузки
        join_depth=1,
        # Черная магия, но иначе отношение будет работать в обе стороны
        # Без лямбды UsersOrm не определено к этому моменту
        remote_side=lambda: [UsersOrm.id],
    )

    updated_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[updated_by_id],
        lazy='joined',
        join_depth=1,
        remote_side=lambda: [UsersOrm.id],
    )

    __table_args__ = (
        UniqueConstraint('username', name='unique_username'),  # Индекс добавляется автоматически
    )

    __order_by__ = (id, )
