from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.domain.user.entities import User
from app.handlers.telegram.start import process_start


def make_container(bot: AsyncMock, user: User) -> AsyncMock:
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        Bot: bot,
        User: user,
    }[dependency]

    return container


def make_message() -> AsyncMock:
    message = AsyncMock(spec=Message)
    message.chat = MagicMock(type="private", id=123)
    message.answer = AsyncMock()

    return message


@pytest.mark.asyncio
async def test_start_shows_regular_user_only_greeting_and_id() -> None:
    bot = AsyncMock(spec=Bot)
    user = User(tg_id=123, username="regular_user")
    message = make_message()
    state = AsyncMock(spec=FSMContext)

    await process_start(
        message,
        state,
        dishka_container=make_container(bot, user),
    )

    message.answer.assert_awaited_once_with(
        "Hello, *regular_user*!\nYour telegram id is `123`!",
    )
    bot.set_my_commands.assert_awaited_once()
    commands = bot.set_my_commands.await_args.args[0]
    assert [command.command for command in commands] == ["start"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [User(tg_id=123, is_staff=True), User(tg_id=123, is_admin=True)],
    ids=["staff", "admin"],
)
async def test_start_shows_role_instructions_and_statistic_for_privileged_user(
    user: User,
) -> None:
    bot = AsyncMock(spec=Bot)
    message = make_message()
    state = AsyncMock(spec=FSMContext)

    await process_start(
        message,
        state,
        dishka_container=make_container(bot, user),
    )

    response = message.answer.await_args.args[0]
    assert "`/statistic`" in response
    assert "*Команды:*" in response
    if user.is_staff:
        assert "*Staff:*" in response
    if user.is_admin:
        assert "*Admin:*" in response

    commands = bot.set_my_commands.await_args.args[0]
    assert [command.command for command in commands] == ["start", "statistic"]
