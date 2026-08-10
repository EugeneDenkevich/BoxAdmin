import logging

from dishka.integrations.aiogram import setup_dishka

from app.bot import get_bot, get_dispatcher
from app.di.containers import default_providers, get_di_container
from app.error_reporter import ErrorReporter
from app.handlers.telegram import pool_router, start_router
from app.logger import configure_logging
from app.middlewaries.aiogram.chat_info import ChatInfoMiddleware
from app.middlewaries.aiogram.create_user_if_not_exists import (
    CreateUserIfNotExistsMiddleware,
)
from app.middlewaries.aiogram.error_handler import ErrorMiddleware
from app.scheduler import setup_scheduler
from app.settings import Settings, get_settings

logger = logging.getLogger(__name__)


async def entrypoint() -> None:
    settings = get_settings()
    configure_logging(log_level=settings.log_level)

    bot = get_bot(settings.bot_token)
    dp = get_dispatcher()

    dp.include_router(start_router)
    dp.include_router(pool_router)

    container = get_di_container(
        *default_providers(),
        context={Settings: settings},
    )

    reporter = ErrorReporter(container=container, bot=bot)

    dp.update.middleware(ErrorMiddleware(reporter=reporter))
    dp.update.middleware(ChatInfoMiddleware())
    dp.update.middleware(CreateUserIfNotExistsMiddleware(container=container))

    setup_dishka(container=container, router=dp, auto_inject=True)
    setup_scheduler(settings=settings, bot=bot, reporter=reporter)

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
