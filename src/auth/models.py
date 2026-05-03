from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.config import settings as s
from database.config import AppBaseClass
from users.models import UsersOrm


class RefreshTokenORM(AppBaseClass):
    """Модель refresh-токенов."""
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(UsersOrm.id, ondelete='CASCADE'), nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String(s.REFRESH_TOKEN_HASH_LENGTH), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[UsersOrm] = relationship(UsersOrm, lazy='joined')

    __table_args__ = (
        UniqueConstraint('refresh_token_hash', name='unique_refresh_token_hash'),
    )
