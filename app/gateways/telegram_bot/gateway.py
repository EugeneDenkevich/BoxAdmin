from app.infra.bot.client import TelegramBotClient


class TelegramBotGateway:
    def __init__(
        self,
        tg_bot_client: TelegramBotClient,
    ) -> None:
        self.tg_bot_client = tg_bot_client

    async def ban_user(self, chat_id: int, tg_user_id: int) -> None:
        await self.tg_bot_client.ban_user(chat_id, tg_user_id)
