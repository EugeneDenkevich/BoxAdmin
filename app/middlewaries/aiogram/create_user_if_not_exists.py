from typing import Any, Awaitable, Callable, Dict, Optional, Union

from aiogram import BaseMiddleware
from aiogram.types import (
    InaccessibleMessage,
    Message,
    PollAnswer,
    TelegramObject,
    Update,
)
from dishka import AsyncContainer, Scope
from dishka.integrations.aiogram import AiogramMiddlewareData

from app.domain.user.entities import User


class CreateUserIfNotExistsMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer) -> None:
        self.container = container

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,  # type: ignore[override]
        data: Dict[str, Any],
    ) -> Any:
        """
        Create user if not exists when he interacts with bot, with a chat in
        which the bot is admin, or votes in an attendance poll.

        :param handler: The handler function to process the event.
        :param event: The Telegram update event.
        :param data: Additional data dictionary.
        :return: The result of the handler function if successful.
        """

        tg_event: Optional[Union[Message, InaccessibleMessage, PollAnswer]] = (
            event.callback_query.message if event.callback_query else event.message
        )
        if tg_event is None:
            tg_event = event.poll_answer

        should_create_user = (isinstance(tg_event, Message) and tg_event.from_user) or (
            isinstance(tg_event, PollAnswer) and tg_event.user
        )

        if should_create_user:
            async with self.container(
                {TelegramObject: tg_event, AiogramMiddlewareData: data},
                scope=Scope.REQUEST,
            ) as request_container:
                await request_container.get(User)

        return await handler(event, data)
