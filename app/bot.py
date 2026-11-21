import logging
from collections.abc import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    MenuButtonCommands,
)

from app.domain.user.entities import User

logger = logging.getLogger(__name__)

START_COMMAND = BotCommand(command="start", description="Показать Telegram ID")
STATISTIC_COMMAND = BotCommand(command="statistic", description="Посещаемость")


def get_bot(token: str) -> Bot:
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )


def get_dispatcher() -> Dispatcher:
    return Dispatcher()


async def setup_bot_menu(bot: Bot) -> None:
    commands = [START_COMMAND]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(
        commands,
        scope=BotCommandScopeAllPrivateChats(),
    )

    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Меню"))


async def setup_user_commands(
    bot: Bot,
    chat_id: int,
    *,
    is_staff_or_admin: bool,
) -> None:
    commands = [START_COMMAND]

    if is_staff_or_admin:
        commands.append(STATISTIC_COMMAND)

    await bot.set_my_commands(
        commands,
        scope=BotCommandScopeChat(chat_id=chat_id),
    )


async def setup_users_commands(bot: Bot, users: Iterable[User]) -> None:
    for user in users:
        if user.tg_id is None:
            continue

        try:
            await setup_user_commands(
                bot,
                user.tg_id,
                is_staff_or_admin=user.is_staff or user.is_admin,
            )
        except TelegramAPIError:
            logger.exception(
                "Failed to update command menu for user %s",
                user.tg_id,
            )
