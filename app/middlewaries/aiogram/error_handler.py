from traceback import format_tb
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InaccessibleMessage, Message, Update
from aiogram.utils.formatting import Bold, Code, Pre, Text
from dishka import AsyncContainer, Scope
from loguru import logger

from app.domain.user.entities import User
from app.services.user.service import UserService


class ErrorMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer) -> None:
        self.container = container

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

            error_traceback = self._get_error_traceback(error)
            error_content = self._get_error_content(error)

            bot: Optional[Bot] = data.get("bot")

            if message and message.chat.type == "private":
                await message.answer("🛠️ Произошла ошибка, мы уже разбираемся. 🙏")

            if bot:
                await self._notify_staff(
                    bot=bot,
                    message=message,
                    error=error,
                    error_content=error_content,
                    error_traceback=error_traceback,
                )

            raise error

    def _get_error_traceback(self, error: Exception) -> str:
        error_traceback = "".join(format_tb(error.__traceback__))
        max_traseback_length = 1000

        if len(error_traceback) > max_traseback_length:
            error_traceback = f"...{error_traceback[-max_traseback_length:]}"

        return error_traceback

    def _get_error_content(self, error: Exception) -> str:
        error_content = str(error)
        max_error_content_length = 150

        if len(error_content) > max_error_content_length:
            error_content = f"{error_content[:max_error_content_length]}..."

        return error_content

    async def _notify_staff(
        self,
        bot: Bot,
        message: Union[Message, InaccessibleMessage, None],
        error: Exception,
        error_content: str,
        error_traceback: str,
    ) -> None:
        staff_users: List[User] = []

        try:
            async with self.container(scope=Scope.REQUEST) as request_container:
                user_servise = await request_container.get(UserService)
                staff_users = await user_servise.get_staff_users()
        except Exception:
            logger.exception("Failed to fetch staff users for error notification")

            return

        if not staff_users:
            return

        if isinstance(message, Message):
            user_id = message.from_user.id if message.from_user else "unknown"
            trigger_info = f"chat_id={message.chat.id}, user_id={user_id}"
        elif message:
            trigger_info = f"chat_id={message.chat.id}, message is inaccessible"
        else:
            trigger_info = "no message context (event had no message/callback_query)"

        staff_text = Text(
            "🚨 Ошибка у пользователя\n",
            Bold("Источник: "),
            Code(trigger_info),
            "\n",
            Bold("Тип: "),
            Code(type(error).__name__),
            "\n",
            Bold("Содержание: "),
            Code(error_content),
            "\n",
            Pre(f"{error_traceback}"),
        ).as_kwargs()

        for staff_user in staff_users:
            if staff_user.tg_id is None:
                continue

            try:
                await bot.send_message(chat_id=staff_user.tg_id, **staff_text)
            except Exception:
                logger.exception("Failed to notify staff user {}", staff_user.tg_id)
