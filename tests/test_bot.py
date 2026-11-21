from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.types import (
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    MenuButtonCommands,
)

from app.bot import setup_bot_menu, setup_user_commands


@pytest.mark.asyncio
async def test_setup_bot_menu_registers_commands_and_menu_button() -> None:
    bot = AsyncMock(spec=Bot)

    await setup_bot_menu(bot)

    assert bot.set_my_commands.await_count == 2
    for call, scope in zip(
        bot.set_my_commands.await_args_list,
        [BotCommandScopeDefault(), BotCommandScopeAllPrivateChats()],
        strict=True,
    ):
        commands = call.args[0]
        assert [(command.command, command.description) for command in commands] == [
            ("start", "Показать Telegram ID"),
        ]
        assert call.kwargs["scope"] == scope

    bot.set_chat_menu_button.assert_awaited_once_with(
        menu_button=MenuButtonCommands(text="Меню"),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("is_staff_or_admin", "expected_commands"),
    [
        (False, ["start"]),
        (True, ["start", "statistic"]),
    ],
)
async def test_setup_user_commands_uses_per_chat_scope(
    is_staff_or_admin: bool,
    expected_commands: list[str],
) -> None:
    bot = AsyncMock(spec=Bot)

    await setup_user_commands(
        bot,
        chat_id=123,
        is_staff_or_admin=is_staff_or_admin,
    )

    bot.set_my_commands.assert_awaited_once()
    call = bot.set_my_commands.await_args
    assert [command.command for command in call.args[0]] == expected_commands
    assert call.kwargs["scope"] == BotCommandScopeChat(chat_id=123)
