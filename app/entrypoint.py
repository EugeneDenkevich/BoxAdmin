import logging

from dishka.integrations.aiogram import setup_dishka

from app.bot import get_bot, get_dispatcher
from app.di.containers import default_providers, get_di_container
from app.routers.telegram import start_router
from app.settings import Settings, get_settings

logger = logging.getLogger(__name__)


async def entrypoint() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    bot = get_bot(settings.bot_token)
    dp = get_dispatcher()

    dp.include_router(start_router)

    container = get_di_container(
        *default_providers(),
        context={Settings: settings},
    )

    setup_dishka(container=container, router=dp, auto_inject=True)

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
