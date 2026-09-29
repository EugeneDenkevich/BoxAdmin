from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domain.pool.entities import Pool
from app.repos.pool.repo import PoolRepo
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
