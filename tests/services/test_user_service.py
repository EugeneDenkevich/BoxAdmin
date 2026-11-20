from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aiogram import Bot
from dishka import Scope

from app.di.containers import default_providers, get_di_container
from app.domain.user.entities import User
from app.gateways.telegram_bot.gateway import TelegramBotGateway
from app.infra.bot.client import TelegramBotClient
from app.repos.user.repo import UserRepo
from app.services.schemas import NonactiveUserCandidate
from app.services.user.service import UserService
from app.settings import Settings


@pytest.mark.asyncio
async def test_ban_user_calls_telegram_through_gateway() -> None:
    bot = AsyncMock(spec=Bot)
    gateway = TelegramBotGateway(TelegramBotClient(bot))
    user_repo = AsyncMock(spec=UserRepo)
    user_repo.get_user_by_tg_id_or_none.return_value = User(tg_id=456)
    uow = AsyncMock()
    service = UserService(
        user_repo=user_repo,
        uow=uow,
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    assert await service.ban_user(456) is True

    bot.ban_chat_member.assert_awaited_once_with(chat_id=-100123, user_id=456)
    banned_user = user_repo.update_user.await_args.args[0]
    assert banned_user.is_banned is True
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_ban_user_propagates_telegram_error() -> None:
    bot = AsyncMock(spec=Bot)
    bot.ban_chat_member.side_effect = RuntimeError("Telegram API error")
    gateway = TelegramBotGateway(TelegramBotClient(bot))
    user_repo = AsyncMock(spec=UserRepo)
    user_repo.get_user_by_tg_id_or_none.return_value = User(tg_id=456)
    uow = AsyncMock()
    service = UserService(
        user_repo=user_repo,
        uow=uow,
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    with pytest.raises(RuntimeError, match="Telegram API error"):
        await service.ban_user(456)

    user_repo.update_user.assert_not_awaited()
    uow.commit.assert_not_awaited()


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


@pytest.mark.parametrize("flag", ["is_admin", "is_staff", "is_banned"])
@pytest.mark.asyncio
async def test_ban_user_skips_admin_staff_and_banned_users(flag: str) -> None:
    bot = AsyncMock(spec=Bot)
    gateway = TelegramBotGateway(TelegramBotClient(bot))
    user_repo = AsyncMock(spec=UserRepo)
    user_repo.get_user_by_tg_id_or_none.return_value = User(
        tg_id=456,
        **{flag: True},
    )
    uow = AsyncMock()
    service = UserService(
        user_repo=user_repo,
        uow=uow,
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    assert await service.ban_user(456) is False

    bot.ban_chat_member.assert_not_awaited()
    user_repo.update_user.assert_not_awaited()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_notify_nonactive_users_sends_staff_a_ban_button() -> None:
    gateway = AsyncMock(spec=TelegramBotGateway)
    user_repo = AsyncMock(spec=UserRepo)
    candidate = NonactiveUserCandidate(
        user_id=uuid4(),
        tg_id=456,
        username="inactive_user",
        missed_pools_count=10,
    )
    user_repo.get_nonactive_users.return_value = [candidate]
    user_repo.get_users.return_value = [
        User(tg_id=101, is_staff=True),
        User(tg_id=202, is_staff=True),
    ]
    service = UserService(
        user_repo=user_repo,
        uow=AsyncMock(),
        bot_gateway=gateway,
        settings=Settings(target_chat=-100123),
    )

    await service.notify_nonactive_users()

    assert gateway.send_message.await_count == 2
    first_message = gateway.send_message.await_args_list[0].kwargs
    assert first_message["chat_id"] == 101
    assert "@inactive_user" in first_message["text"]
    assert str(candidate.user_id) in first_message["text"]
    assert "10 пулов" in first_message["text"]
    button = first_message["reply_markup"].inline_keyboard[0][0]
    assert button.text == "Забанить"
    assert button.callback_data == "nonactive_ban:456"
