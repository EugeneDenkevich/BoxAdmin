from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa

from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.infra.db.tables.user import UserTable
from app.repos.base import BaseRepo
from app.repos.user.converters import user_db_to_entity


class UserRepo(BaseRepo):
    async def save_user(self, user: User) -> None:
        self.session.add(UserTable(**user.model_dump()))

        await self.session.flush()

    async def get_user_or_none(self, user_id: UUID) -> Optional[User]:
        query = sa.select(UserTable).where(UserTable.id == user_id)
        user = await self._get_or_none(query)

        return user_db_to_entity(user) if user else None

    async def get_user(self, user_id: UUID) -> User:
        user = await self.get_user_or_none(user_id=user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_user_by_tg_id_or_none(self, tg_id: int) -> Optional[User]:
        query = sa.select(UserTable).where(UserTable.tg_id == tg_id)
        user = await self._get_or_none(query)

        return user_db_to_entity(user) if user else None

    async def get_user_by_tg_id(self, tg_id: int) -> User:
        user = await self.get_user_by_tg_id_or_none(tg_id=tg_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def update_user(self, user: User) -> None:
        query = (
            sa.update(UserTable)
            .where(UserTable.id == user.id)
            .values(**user.model_dump(exclude={"id"}))
        )

        await self.session.execute(query)

    async def get_users(self) -> List[User]:
        query = sa.select(UserTable)
        result = await self.session.execute(query)

        return [user_db_to_entity(user) for user in result.scalars()]
