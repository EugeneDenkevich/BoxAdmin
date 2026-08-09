from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

bot: Optional[Bot] = None
dispatcher: Optional[Dispatcher] = None


def get_bot(token: str) -> Bot:
    global bot

    if bot is None:
        bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        )

    return bot


def get_dispatcher() -> Dispatcher:
    global dispatcher

    if dispatcher is None:
        dispatcher = Dispatcher()

    return dispatcher
