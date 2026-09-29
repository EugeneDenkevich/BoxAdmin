from unittest.mock import AsyncMock

import pytest
from aiogram.types import PollAnswer
from aiogram.types import User as TelegramUser

from app.domain.pool.exceptions import PoolNotFoundError
from app.domain.user.entities import User
from app.handlers.telegram.pool import handle_poll_answer
from app.services.pool.service import PoolService


@pytest.mark.asyncio
async def test_poll_answer_injects_dependencies_and_saves_vote() -> None:
    user = User(tg_id=111)
    pool_service = AsyncMock(spec=PoolService)
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        User: user,
        PoolService: pool_service,
    }[dependency]
    poll_answer = PollAnswer(
        poll_id="poll-1",
        user=TelegramUser(id=111, is_bot=False, first_name="Test"),
        option_ids=[0],
        option_persistent_ids=["0"],
    )

    await handle_poll_answer(poll_answer, dishka_container=container)

    pool_service.save_vote.assert_awaited_once_with(
        telegram_poll_id="poll-1",
        user_id=user.id,
        option_ids=[0],
    )


@pytest.mark.asyncio
async def test_retracted_poll_answer_saves_empty_options() -> None:
    user = User(tg_id=111)
    pool_service = AsyncMock(spec=PoolService)
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        User: user,
        PoolService: pool_service,
    }[dependency]
    poll_answer = PollAnswer(
        poll_id="poll-1",
        user=TelegramUser(id=111, is_bot=False, first_name="Test"),
        option_ids=[],
        option_persistent_ids=[],
    )

    await handle_poll_answer(poll_answer, dishka_container=container)

    pool_service.save_vote.assert_awaited_once_with(
        telegram_poll_id="poll-1",
        user_id=user.id,
        option_ids=[],
    )


@pytest.mark.asyncio
async def test_poll_answer_for_unknown_poll_is_ignored() -> None:
    user = User(tg_id=111)
    pool_service = AsyncMock(spec=PoolService)
    pool_service.save_vote.side_effect = PoolNotFoundError()
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        User: user,
        PoolService: pool_service,
    }[dependency]
    poll_answer = PollAnswer(
        poll_id="unknown-poll",
        user=TelegramUser(id=111, is_bot=False, first_name="Test"),
        option_ids=[0],
        option_persistent_ids=["0"],
    )

    await handle_poll_answer(poll_answer, dishka_container=container)

    pool_service.save_vote.assert_awaited_once_with(
        telegram_poll_id="unknown-poll",
        user_id=user.id,
        option_ids=[0],
    )
