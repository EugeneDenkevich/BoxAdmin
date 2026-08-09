from typing import List, Optional, cast
from uuid import UUID

from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.infra.uow import UoW
from app.repos.user.repo import UserRepo
from app.services.base import BaseService
from app.services.user.schemas import UpdateUserData


class UserService(BaseService):
    def __init__(self, user_repo: UserRepo, uow: UoW) -> None:
        self.user_repo = user_repo
        self.uow = uow

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

        updated_user = self._update_by_data(user, data)

        await self.user_repo.update_user(cast(User, updated_user))
        await self.uow.commit()

        return user

    async def get_staff_users(self) -> List[User]:
        return await self.user_repo.get_users(is_staff=True)
