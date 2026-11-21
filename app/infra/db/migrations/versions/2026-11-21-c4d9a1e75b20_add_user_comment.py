"""add comment to users

Revision ID: c4d9a1e75b20
Revises: b69243fe7281
Create Date: 2026-11-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d9a1e75b20"
down_revision: Union[str, None] = "b69243fe7281"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("comment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "comment")
