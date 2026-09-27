from aiogram import Bot

from app.repos.user.repo import UserRepo
from app.services.user.service import UserService


class BanNonactiveUsers:
    def __init__(self, user_repo: UserRepo, user_service: UserService) -> None:
        self.user_repo = user_repo
        self.user_service = user_service

    async def __call__(self, bot: Bot, chat_id: int) -> None:
        tg_user_ids = await self.user_repo.get_nonactive_user_tg_ids()
        for tg_user_id in tg_user_ids:
            await self.user_service.ban_user(bot, chat_id, tg_user_id)
