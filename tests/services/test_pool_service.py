from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.pool.entities import Pool
from app.repos.pool.repo import PoolRepo
from app.schemas import PoolAttendanceVote
from app.services.pool.service import PoolService


@pytest.mark.asyncio
async def test_save_vote_gets_pool_and_commits() -> None:
    repo = AsyncMock(spec=PoolRepo)
    pool = Pool(telegram_poll_id="poll")
    repo.get_pool.return_value = pool
    uow = AsyncMock()
    user_id = uuid4()
    service = PoolService(repo, uow)

    await service.save_vote("poll", user_id, [0])

    repo.get_pool.assert_awaited_once_with("poll")
    repo.save_vote.assert_awaited_once_with(pool.id, user_id, [0])
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_vote_saves_retracted_answer() -> None:
    repo = AsyncMock(spec=PoolRepo)
    pool = Pool(telegram_poll_id="poll")
    repo.get_pool.return_value = pool
    uow = AsyncMock()
    user_id = uuid4()
    service = PoolService(repo, uow)

    await service.save_vote("poll", user_id, [])

    repo.get_pool.assert_awaited_once_with("poll")
    repo.save_vote.assert_awaited_once_with(pool.id, user_id, [])
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_attendance_votes_delegates_to_repo() -> None:
    votes = [
        PoolAttendanceVote(
            pool_id=uuid4(),
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            option_ids=[0],
        ),
    ]
    repo = AsyncMock(spec=PoolRepo)
    repo.get_attendance_votes.return_value = votes
    service = PoolService(repo, AsyncMock())

    result = await service.get_attendance_votes()

    assert result == votes
    repo.get_attendance_votes.assert_awaited_once_with()
