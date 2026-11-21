from typing import List, Optional, cast
from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.gateways.telegram_bot.gateway import TelegramBotGateway
from app.infra.uow import UoW
from app.repos.user.repo import UserRepo
from app.schemas import NonactiveUserCandidate
from app.services.base import BaseService
from app.services.user.schemas import UpdateUserData
from app.settings import Settings


class UserService(BaseService):
    def __init__(
        self,
        user_repo: UserRepo,
        uow: UoW,
        bot_gateway: TelegramBotGateway,
        settings: Settings,
    ) -> None:
        self.user_repo = user_repo
        self.uow = uow
        self.bot_gateway = bot_gateway
        self.target_chat = settings.target_chat

    async def get_user_by_tg_id(
        self,
        tg_id: int,
    ) -> User:
        user = await self.user_repo.get_user_by_tg_id_or_none(tg_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_or_create_tg_user(
        self,
        tg_id: int,
        username: Optional[str] = None,
    ) -> User:
        user = await self.user_repo.get_user_by_tg_id_or_none(tg_id)

        if user is None:
            user = User(tg_id=tg_id, username=username)

            await self.user_repo.save_user(user)
            await self.uow.commit()

        return user

    async def get_user_or_none(self, user_id: UUID) -> Optional[User]:
        return await self.user_repo.get_user_or_none(user_id)

    async def update_user(self, data: UpdateUserData) -> User:
        user = await self.user_repo.get_user_or_none(data.user_id)

        if user is None:
            raise UserNotFoundError()

        updated_user = self._update(user, data)

        await self.user_repo.update_user(cast(User, updated_user))
        await self.uow.commit()

        return user

    async def get_staff_users(self) -> List[User]:
        return await self.user_repo.get_users(is_staff=True)

    async def ban_user(self, tg_id: int) -> bool:
        user = await self.get_user_by_tg_id(tg_id)

        if user.is_admin or user.is_staff or user.is_banned:
            logger.info("User is admin, staff or already banned, skip banning")

            return False

        await self.bot_gateway.ban_user(self.target_chat, tg_id)

        logger.info("User was banned: [USER_ID: {}]", user.id)

        banned_user = user.model_copy(update={"is_banned": True})

        await self.user_repo.update_user(banned_user)
        await self.uow.commit()

        return True

    async def get_nonactive_users(self) -> List[NonactiveUserCandidate]:
        return await self.user_repo.get_nonactive_users()

    async def is_nonactive_user(self, tg_id: int) -> bool:
        return await self.user_repo.is_nonactive_user(tg_id)

    async def notify_nonactive_users(self) -> None:
        nonactive_users = await self.get_nonactive_users()
        staff_users = await self.get_staff_users()

        if not staff_users:
            logger.warning("No staff users to notify about nonactive users")

            return

        for nonactive_user in nonactive_users:
            await self._notify_staff_about_nonactive_user(
                nonactive_user,
                staff_users,
            )

    async def _notify_staff_about_nonactive_user(
        self,
        nonactive_user: NonactiveUserCandidate,
        staff_users: List[User],
    ) -> None:
        display_name = (
            f"@{nonactive_user.username}"
            if nonactive_user.username
            else f"Telegram ID {nonactive_user.tg_id}"
        )

        message = (
            f"Пользователь {display_name} (Telegram ID: {nonactive_user.tg_id})\n"
            f"ID в БД: {nonactive_user.user_id}\n"
            f"Пропустил {nonactive_user.missed_pools_count} пулов подряд. Баним?"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Забанить",
                        callback_data=f"nonactive_ban:{nonactive_user.tg_id}",
                    ),
                ],
            ],
        )

        for staff_user in staff_users:
            if staff_user.tg_id is None:
                continue

            try:
                await self.bot_gateway.send_message(
                    chat_id=staff_user.tg_id,
                    text=message,
                    reply_markup=keyboard,
                )
            except Exception:
                logger.exception(
                    "Failed to notify staff user {} about nonactive user {}",
                    staff_user.tg_id,
                    nonactive_user.tg_id,
                )
