from typing import AsyncGenerator, Optional

from aiogram.types import Message, PollAnswer, TelegramObject
from dishka import Provider, Scope, provide

from app.domain.user.entities import User
from app.usecases.user.get_or_create_user import GetOrCreateTgUserUseCase


class UserProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_user(
        self,
        tg_event: TelegramObject,
        get_or_create_tg_user: GetOrCreateTgUserUseCase,
    ) -> AsyncGenerator[User]:
        tg_id: Optional[int] = None
        username: Optional[str] = None

        if isinstance(tg_event, Message) and tg_event.from_user:
            tg_id = tg_event.from_user.id
            username = tg_event.from_user.username
        elif isinstance(tg_event, PollAnswer) and tg_event.user:
            tg_id = tg_event.user.id
            username = tg_event.user.username

        if tg_id is not None:
            yield await get_or_create_tg_user(tg_id=tg_id, username=username)
