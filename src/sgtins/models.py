from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import CheckConstraint, Computed, DateTime, Index, Integer, String, UniqueConstraint, func, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings as s
from database.config import AppBaseClass


class SgtinStatus(StrEnum):
    """Возможные статусы кода маркировки."""
    ISSUED = auto()
    PRINTED = auto()
    EXPIRED = auto()


class SgtinOrm(AppBaseClass):
    """Модель таблицы кодов маркировки.

    Проверка на наличие у продуктов в БД  добавляемого GTIN реализована на уровне приложения.
    """
    __tablename__ = 'sgtins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    gtin: Mapped[str] = mapped_column(String(s.GTIN_LENGTH), nullable=False)
    sgtin: Mapped[str] = mapped_column(String(s.SGTIN_LENGTH), nullable=False)
    crypto_end: Mapped[str] = mapped_column(String(s.CRYPTO_END_LENGTH), nullable=False)

    status: Mapped[SgtinStatus] = mapped_column(SQLEnum(SgtinStatus, name='sgtin_status_enum'), default=SgtinStatus.ISSUED, server_default=text("'ISSUED'"), nullable=False)

    # Здесь даты достаточно, время избыточно
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    shelf_life: Mapped[int] = mapped_column(Integer, default=s.SGTIN_SHELF_LIFE, server_default=text(str(s.SGTIN_SHELF_LIFE)), nullable=False)
    printed_at: Mapped[datetime] = mapped_column(DateTime, default=None, server_default=text('NULL'), nullable=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime, Computed("created_at + shelf_life * INTERVAL '1 day'", persisted=True), nullable=False)

    __table_args__ = (
        CheckConstraint(func.length(gtin) == s.GTIN_LENGTH, name='gtin_length'),
        CheckConstraint(func.length(sgtin) == s.SGTIN_LENGTH, name='sgtin_length'),
        CheckConstraint(func.length(crypto_end) == s.CRYPTO_END_LENGTH, name='crypto_end_length'),
        UniqueConstraint('sgtin', 'crypto_end', name='unique_sgtin_crypto_end'),  # Индекс добавляется автоматически
        Index('ix_sgtins_gtin', 'gtin'),
        Index('ix_sgtins_gtin_status', 'gtin', 'status'),
    )

    __order_by__ = (id, )
