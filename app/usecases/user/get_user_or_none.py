from typing import Optional
from uuid import UUID

from app.domain.user.entities import User
from app.services.user.service import UserService


class GetUserOrNoneUseCase:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    async def __call__(self, user_id: UUID) -> Optional[User]:
        return await self._user_service.get_user_or_none(user_id)
