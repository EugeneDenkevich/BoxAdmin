from unittest.mock import AsyncMock, call

import pytest
from aiogram import Bot

from app.usecases.user.ban_nonactive_users import BanNonactiveUsers


@pytest.mark.asyncio
async def test_bans_users_returned_by_repository() -> None:
    bot = AsyncMock(spec=Bot)
    user_repo = AsyncMock()
    user_repo.get_nonactive_user_tg_ids.return_value = [111, 222]
    user_service = AsyncMock()
    use_case = BanNonactiveUsers(user_repo, user_service)

    await use_case(bot, -100123)

    assert user_service.ban_user.await_args_list == [
        call(bot, -100123, 111),
        call(bot, -100123, 222),
    ]


@pytest.mark.asyncio
async def test_does_not_ban_when_repository_returns_no_users() -> None:
    user_repo = AsyncMock()
    user_repo.get_nonactive_user_tg_ids.return_value = []
    user_service = AsyncMock()
    use_case = BanNonactiveUsers(user_repo, user_service)

    await use_case(AsyncMock(spec=Bot), -100123)

    user_service.ban_user.assert_not_awaited()
