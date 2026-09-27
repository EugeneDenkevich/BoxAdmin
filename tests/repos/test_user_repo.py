from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infra.db.base import BaseTable
from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.infra.db.tables.user import UserTable
from app.repos.user.repo import UserRepo


@pytest.mark.asyncio
async def test_get_nonactive_user_tg_ids_returns_only_eligible_nonvoters() -> None:
    engine = sa.create_engine("sqlite+pysqlite:///:memory:")
    BaseTable.metadata.create_all(engine)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    inactive_id = uuid4()
    active_id = uuid4()
    recent_id = uuid4()
    pool_ids = [uuid4() for _ in range(12)]

    with Session(engine) as db_session:
        db_session.add_all(
            [
                UserTable(
                    id=inactive_id,
                    tg_id=101,
                    username=None,
                    is_admin=False,
                    is_staff=False,
                    created_at=now,
                    updated_at=now,
                ),
                UserTable(
                    id=active_id,
                    tg_id=202,
                    username=None,
                    is_admin=False,
                    is_staff=False,
                    created_at=now,
                    updated_at=now,
                ),
                UserTable(
                    id=recent_id,
                    tg_id=303,
                    username=None,
                    is_admin=False,
                    is_staff=False,
                    created_at=now + timedelta(days=9),
                    updated_at=now + timedelta(days=9),
                ),
            ],
        )
        db_session.add_all(
            [
                PoolTable(
                    id=pool_id,
                    telegram_poll_id=f"poll-{index}",
                    created_at=now + timedelta(days=index + 1),
                    updated_at=now + timedelta(days=index + 1),
                )
                for index, pool_id in enumerate(pool_ids)
            ],
        )
        db_session.add(
            UserPoolTable(
                user_id=active_id,
                pool_id=pool_ids[-1],
                option_ids=[0],
            ),
        )
        db_session.commit()

        async_session = AsyncMock(spec=AsyncSession)
        async_session.execute.side_effect = lambda query: db_session.execute(query)
        repo = UserRepo(async_session)

        assert await repo.get_nonactive_user_tg_ids() == [101]
        async_session.execute.assert_awaited_once()

    engine.dispose()
