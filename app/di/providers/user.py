from typing import AsyncGenerator

from aiogram.types import Message, TelegramObject
from dishka import Provider, provide, Scope

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
        if isinstance(tg_event, Message) and tg_event.from_user:
            yield await get_or_create_tg_user(
                tg_id=tg_event.from_user.id,
                username=tg_event.from_user.username,
            )
