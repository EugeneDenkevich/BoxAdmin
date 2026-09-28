from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from dishka import Scope

from app.di.containers import default_providers, get_di_container
from app.gateways.telegram_bot.gateway import TelegramBotGateway
from app.infra.bot.client import TelegramBotClient
from app.services.user.service import UserService
from app.settings import Settings


@pytest.mark.asyncio
async def test_ban_user_calls_telegram_through_gateway() -> None:
    bot = AsyncMock(spec=Bot)
    gateway = TelegramBotGateway(TelegramBotClient(bot))
    service = UserService(
        user_repo=AsyncMock(),
        uow=AsyncMock(),
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    await service.ban_user(456)

    bot.ban_chat_member.assert_awaited_once_with(chat_id=-100123, user_id=456)


@pytest.mark.asyncio
async def test_ban_user_propagates_telegram_error() -> None:
    bot = AsyncMock(spec=Bot)
    bot.ban_chat_member.side_effect = RuntimeError("Telegram API error")
    gateway = TelegramBotGateway(TelegramBotClient(bot))
    service = UserService(
        user_repo=AsyncMock(),
        uow=AsyncMock(),
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    with pytest.raises(RuntimeError, match="Telegram API error"):
        await service.ban_user(456)


@pytest.mark.asyncio
async def test_di_shares_bot_with_client_and_gateway() -> None:
    settings = Settings(bot_token="123456:TESTTOKEN", target_chat=-100123)
    container = get_di_container(
        *default_providers(),
        context={Settings: settings},
    )
    try:
        bot = await container.get(Bot)
        client = await container.get(TelegramBotClient)
        async with container(scope=Scope.REQUEST) as request_container:
            gateway = await request_container.get(TelegramBotGateway)

        assert client.bot is bot
        assert gateway.tg_bot_client is client
    finally:
        await container.close()
