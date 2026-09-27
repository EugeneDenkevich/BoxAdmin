from app.services.user.service import UserService


class BanNonactiveUsers:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def __call__(self) -> None:
        tg_user_ids = await self.user_service.get_nonactive_user_tg_ids()

        for tg_user_id in tg_user_ids:
            await self.user_service.ban_user(tg_user_id)
