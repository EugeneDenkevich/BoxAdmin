from unittest.mock import AsyncMock

import pytest
from aiogram import Bot

from app.services.user.service import UserService


@pytest.mark.asyncio
async def test_ban_user_calls_telegram() -> None:
    bot = AsyncMock(spec=Bot)
    service = UserService(user_repo=AsyncMock(), uow=AsyncMock())

    await service.ban_user(bot, -100123, 456)

    bot.ban_chat_member.assert_awaited_once_with(chat_id=-100123, user_id=456)


@pytest.mark.asyncio
async def test_ban_user_propagates_telegram_error() -> None:
    bot = AsyncMock(spec=Bot)
    bot.ban_chat_member.side_effect = RuntimeError("Telegram API error")
    service = UserService(user_repo=AsyncMock(), uow=AsyncMock())

    with pytest.raises(RuntimeError, match="Telegram API error"):
        await service.ban_user(bot, -100123, 456)
