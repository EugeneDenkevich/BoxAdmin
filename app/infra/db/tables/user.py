from datetime import datetime
from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import BaseTable


class UserTable(BaseTable):
    """Table for User entity."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(sa.Uuid, primary_key=True)
    """ID."""

    tg_id: Mapped[Optional[int]] = mapped_column(
        sa.BigInteger,
        nullable=True,
        unique=True,
    )
    """Telegram ID of current user"""

    username: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    """Telegram username"""

    is_admin: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    """Is the user admin"""

    is_staff: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    """Is the user staff (receives error/monitoring notifications)"""

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
    )
    """Date and time of creation"""

    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
    )
    """Date and time of updating"""
