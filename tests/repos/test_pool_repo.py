from datetime import datetime, timezone
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.domain.pool.exceptions import PoolNotFoundError
from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.infra.db.tables.user import UserTable
from app.repos.pool.repo import PoolRepo


@pytest.mark.asyncio
async def test_get_pool_and_update_vote(test_database_url: URL) -> None:
    engine = create_async_engine(test_database_url)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    user_id = uuid4()
    pool_id = uuid4()

    try:
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
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_pool_raises_if_missing(test_database_url: URL) -> None:
    engine = create_async_engine(test_database_url)
    try:
        async with AsyncSession(engine) as session:
            with pytest.raises(PoolNotFoundError):
                await PoolRepo(session).get_pool("missing")
    finally:
        await engine.dispose()
