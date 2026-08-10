from traceback import format_tb
from typing import List

from aiogram import Bot
from aiogram.utils.formatting import Bold, Code, Pre, Text
from dishka import AsyncContainer, Scope
from loguru import logger

from app.domain.user.entities import User
from app.services.user.service import UserService


class ErrorReporter:
    def __init__(self, container: AsyncContainer, bot: Bot) -> None:
        self.container = container
        self.bot = bot

    async def report(self, error: Exception, *, context: str) -> None:
        error_traceback = self._get_error_traceback(error)
        error_content = self._get_error_content(error)

        staff_users = await self._get_staff_users()

        if not staff_users:
            return

        staff_text = Text(
            "🚨 Ошибка в приложении\n",
            Bold("Источник: "),
            Code(context),
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
                await self.bot.send_message(chat_id=staff_user.tg_id, **staff_text)
            except Exception:
                logger.exception("Failed to notify staff user {}", staff_user.tg_id)

    async def _get_staff_users(self) -> List[User]:
        try:
            async with self.container(scope=Scope.REQUEST) as request_container:
                user_service = await request_container.get(UserService)

                return await user_service.get_staff_users()
        except Exception:
            logger.exception("Failed to fetch staff users for error notification")

            return []

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
