from aiogram import Bot


class TelegramBotClient:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def ban_user(self, chat_id: int, tg_user_id: int) -> None:
        await self.bot.ban_chat_member(chat_id=chat_id, user_id=tg_user_id)
