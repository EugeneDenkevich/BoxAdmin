from typing import Optional

from app.domain.user.entities import User
from app.services.user.service import UserService


class GetOrCreateTgUserUseCase:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    async def __call__(self, tg_id: int, username: Optional[str] = None) -> User:
        return await self._user_service.get_or_create_tg_user(tg_id, username)
