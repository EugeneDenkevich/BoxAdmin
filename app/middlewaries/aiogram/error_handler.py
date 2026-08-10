from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, Update

from app.error_reporter import ErrorReporter


class ErrorMiddleware(BaseMiddleware):
    def __init__(self, reporter: ErrorReporter) -> None:
        self.reporter = reporter

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: Dict[str, Any],
    ) -> Any:
        """
        Middleware to handle exceptions during event processing.

        :param handler: The handler function to process the event.
        :param event: The Telegram update event.
        :param data: Additional data dictionary.
        :return: The result of the handler function if successful.
        """

        try:
            return await handler(event, data)
        except Exception as error:
            if event.callback_query:
                try:
                    await event.callback_query.answer()
                except TelegramBadRequest:
                    pass

                message = event.callback_query.message
            else:
                message = event.message

            if message and message.chat.type == "private":
                await message.answer("🛠️ Произошла ошибка, мы уже разбираемся. 🙏")

            if isinstance(message, Message):
                user_id = message.from_user.id if message.from_user else "unknown"
                trigger_info = f"chat_id={message.chat.id}, user_id={user_id}"
            elif message:
                trigger_info = f"chat_id={message.chat.id}, message is inaccessible"
            else:
                trigger_info = (
                    "no message context (event had no message/callback_query)"
                )

            await self.reporter.report(error, context=trigger_info)

            raise error
