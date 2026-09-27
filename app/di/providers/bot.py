from collections.abc import AsyncIterator

from aiogram import Bot
from dishka import Provider, Scope, provide

from app.bot import get_bot
from app.gateways.telegram_bot.gateway import TelegramBotGateway
from app.infra.bot.client import TelegramBotClient
from app.settings import Settings


class TelegramBotProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_bot(self, settings: Settings) -> AsyncIterator[Bot]:
        bot = get_bot(settings.bot_token)

        try:
            yield bot
        finally:
            await bot.session.close()

    @provide(scope=Scope.APP)
    def provide_bot_client(self, bot: Bot) -> TelegramBotClient:
        return TelegramBotClient(bot=bot)

    @provide(scope=Scope.REQUEST)
    def provide_bot_gateway(
        self,
        tg_bot_client: TelegramBotClient,
    ) -> TelegramBotGateway:
        return TelegramBotGateway(tg_bot_client=tg_bot_client)
