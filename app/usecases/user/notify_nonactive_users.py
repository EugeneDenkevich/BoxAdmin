from app.services.user.service import UserService


class NotifyNonactiveUsersUseCasse:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def __call__(self) -> None:
        await self.user_service.notify_nonactive_users()
