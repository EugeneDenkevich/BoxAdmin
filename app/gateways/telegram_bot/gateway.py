from typing import Any

from app.infra.bot.client import TelegramBotClient


class TelegramBotGateway:
    def __init__(
        self,
        tg_bot_client: TelegramBotClient,
    ) -> None:
        self.tg_bot_client = tg_bot_client

    async def ban_user(self, chat_id: int, tg_user_id: int) -> None:
        await self.tg_bot_client.ban_user(chat_id, tg_user_id)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Any,
    ) -> None:
        await self.tg_bot_client.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )
