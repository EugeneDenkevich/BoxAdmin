from app.domain.user.entities import User
from app.services.user.schemas import UpdateUserData
from app.services.user.service import UserService

class UpdateUserUseCase:
    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    async def __call__(self, data: UpdateUserData) -> User:
        return await self._user_service.update_user(data)
