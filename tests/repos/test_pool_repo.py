from datetime import datetime, timezone
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.domain.pool.exceptions import PoolNotFoundError
from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.infra.db.tables.user import UserTable
from app.repos.pool.repo import PoolRepo


@pytest.mark.asyncio
async def test_get_pool_and_update_vote(engine: AsyncEngine) -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    user_id = uuid4()
    pool_id = uuid4()

    async with AsyncSession(engine) as session:
        session.add(
            UserTable(
                id=user_id,
                tg_id=404,
                username=None,
                is_admin=False,
                is_staff=False,
                created_at=now,
                updated_at=now,
            ),
        )
        session.add(
            PoolTable(
                id=pool_id,
                telegram_poll_id="pool-for-vote",
                created_at=now,
                updated_at=now,
            ),
        )

        await session.flush()
        repo = PoolRepo(session)

        assert (await repo.get_pool("pool-for-vote")).id == pool_id
        await repo.save_vote(pool_id, user_id, [0])
        await repo.save_vote(pool_id, user_id, [1])

        votes = (
            await session.execute(
                sa.select(UserPoolTable).where(UserPoolTable.user_id == user_id),
            )
        ).scalars().all()

        assert len(votes) == 1
        assert votes[0].option_ids == [1]


@pytest.mark.asyncio
async def test_get_pool_raises_if_missing(engine: AsyncEngine) -> None:
    async with AsyncSession(engine) as session:
        with pytest.raises(PoolNotFoundError):
            await PoolRepo(session).get_pool("missing")
