from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from loguru import logger


class ChatInfoMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: Dict[str, Any],
    ) -> Any:
        """
        Logs detailed chat info in which the user sent the message.

        :param handler: The handler function to process the event.
        :param event: The Telegram update event.
        :param data: Additional data dictionary.
        :return: The result of the handler function if successful.
        """

        message = (
            event.callback_query.message if event.callback_query else event.message
        )

        if isinstance(message, Message):
            chat = message.chat
            tg_user = message.from_user

            logger.info(
                "Update from chat [CHAT_ID: {}, TYPE: {}, TITLE: {}] "
                "by user [TG_ID: {}, USERNAME: {}]",
                chat.id,
                chat.type,
                chat.title,
                tg_user.id if tg_user else None,
                tg_user.username if tg_user else None,
            )

        return await handler(event, data)
