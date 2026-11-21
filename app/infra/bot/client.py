from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.schemas import InlineKeyboardMarkupSchema


class TelegramBotClient:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def ban_user(self, chat_id: int, tg_user_id: int) -> None:
        await self.bot.ban_chat_member(chat_id=chat_id, user_id=tg_user_id)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkupSchema,
    ) -> None:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data,
                    )
                    for button in row
                ]
                for row in reply_markup.inline_keyboard
            ],
        )

        await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup,
        )
