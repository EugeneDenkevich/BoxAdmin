"""add pool and user vote history

Revision ID: 9d682fc137a1
Revises: 18a5ac1032ed
Create Date: 2026-09-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9d682fc137a1"
down_revision: Union[str, None] = "18a5ac1032ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        "pools",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("telegram_poll_id", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_poll_id"),
    )
    op.create_index("ix_pools_created_at", "pools", ["created_at"])
    op.create_table(
        "users_pools",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("pool_id", sa.Uuid(), nullable=False),
        sa.Column("option_ids", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["pool_id"], ["pools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "pool_id"),
    )


def downgrade() -> None:
    op.drop_table("users_pools")
    op.drop_index("ix_pools_created_at", table_name="pools")
    op.drop_table("pools")
