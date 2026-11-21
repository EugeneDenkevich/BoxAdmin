from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.infra.db.tables.user import UserTable
from app.repos.user.repo import UserRepo


@pytest.mark.asyncio
async def test_get_nonactive_users_returns_only_eligible_nonvoters(
    engine: AsyncEngine,
) -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    inactive_id = uuid4()
    active_id = uuid4()
    recent_id = uuid4()
    admin_id = uuid4()
    staff_id = uuid4()
    banned_id = uuid4()
    pool_ids = [uuid4() for _ in range(12)]

    async with AsyncSession(engine) as session:
        session.add_all(
            [
                UserTable(
                    id=user_id,
                    tg_id=tg_id,
                    username=None,
                    is_admin=is_admin,
                    is_staff=is_staff,
                    is_banned=is_banned,
                    created_at=created_at,
                    updated_at=created_at,
                )
                for user_id, tg_id, created_at, is_admin, is_staff, is_banned in (
                    (inactive_id, 101, now, False, False, False),
                    (active_id, 202, now, False, False, False),
                    (recent_id, 303, now + timedelta(days=9), False, False, False),
                    (admin_id, 404, now, True, False, False),
                    (staff_id, 505, now, False, True, False),
                    (banned_id, 606, now, False, False, True),
                )
            ],
        )
        session.add_all(
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
        await session.flush()
        session.add(
            UserPoolTable(
                user_id=active_id,
                pool_id=pool_ids[-1],
                option_ids=[0],
            ),
        )
        await session.flush()

        repo = UserRepo(session)
        candidates = await repo.get_nonactive_users()

        assert len(candidates) == 1
        assert candidates[0].user_id == inactive_id
        assert candidates[0].tg_id == 101
        assert candidates[0].missed_pools_count == 10
        assert await repo.is_nonactive_user(101) is True
        assert await repo.is_nonactive_user(202) is False


@pytest.mark.asyncio
async def test_update_user_persists_ban_status_and_updated_at(
    engine: AsyncEngine,
) -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    user_id = uuid4()

    async with AsyncSession(engine) as session:
        session.add(
            UserTable(
                id=user_id,
                tg_id=404,
                username=None,
                is_admin=False,
                is_staff=False,
                is_banned=False,
                created_at=now,
                updated_at=now,
            ),
        )
        await session.flush()
        repo = UserRepo(session)
        user = await repo.get_user_by_tg_id_or_none(404)
        assert user is not None

        await repo.update_user(user.model_copy(update={"is_banned": True}))
        await session.commit()

        updated_user = await repo.get_user_by_tg_id_or_none(404)
        assert updated_user is not None
        assert updated_user.is_banned is True
        assert updated_user.updated_at > now
