from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.types import MenuButtonCommands

from app.bot import setup_bot_menu


@pytest.mark.asyncio
async def test_setup_bot_menu_registers_commands_and_menu_button() -> None:
    bot = AsyncMock(spec=Bot)

    await setup_bot_menu(bot)

    bot.set_my_commands.assert_awaited_once()
    commands = bot.set_my_commands.await_args.args[0]
    assert [(command.command, command.description) for command in commands] == [
        ("start", "Показать Telegram ID"),
        ("statistic", "Посещаемость"),
    ]
    bot.set_chat_menu_button.assert_awaited_once_with(
        menu_button=MenuButtonCommands(text="Меню"),
    )
