from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import BaseTable


class PoolTable(BaseTable):
    __tablename__ = "pools"

    id: Mapped[UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid4)
    telegram_poll_id: Mapped[str] = mapped_column(
        sa.String(256),
        nullable=False,
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class UserPoolTable(BaseTable):
    __tablename__ = "users_pools"

    user_id: Mapped[UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    pool_id: Mapped[UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("pools.id", ondelete="CASCADE"),
        primary_key=True,
    )
    option_ids: Mapped[list[int]] = mapped_column(sa.JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
