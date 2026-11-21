from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, MenuButtonCommands


def get_bot(token: str) -> Bot:
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )


def get_dispatcher() -> Dispatcher:
    return Dispatcher()


async def setup_bot_menu(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Показать Telegram ID"),
            BotCommand(command="statistic", description="Посещаемость"),
        ],
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="Меню"))
