from typing import List, Optional, cast
from uuid import UUID

import sqlalchemy as sa

from app.domain.user.entities import User
from app.domain.user.exceptions import UserNotFoundError
from app.infra.db.tables.pool import PoolTable, UserPoolTable
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

    async def get_users(
        self,
        is_staff: Optional[bool] = None,
    ) -> List[User]:
        query = sa.select(UserTable)

        if is_staff is not None:
            query = query.where(UserTable.is_staff == is_staff)

        result = await self.session.execute(query)

        return [user_db_to_entity(user) for user in result.scalars()]

    async def get_nonactive_user_tg_ids(self) -> List[int]:
        """
        Взять id пользователей, которые не учавствовали в необходимом кол-ве
        подряд идущих пулов (required_pools_count).
        """

        required_pools_count = 10

        # fmt:off
        latest_pools = (
            sa
            .select(
                PoolTable.id.label("pool_id"),
                PoolTable.created_at.label("created_at"),
            )
            .order_by(PoolTable.created_at.desc(), PoolTable.id.desc())
            .limit(required_pools_count)
            .cte("latest_pools")
        )

        query = (
            sa
            .select(UserTable.tg_id)
            .select_from(UserTable)
            .join(latest_pools, latest_pools.c.created_at > UserTable.created_at)
            .outerjoin(
                UserPoolTable,
                sa.and_(
                    UserPoolTable.user_id == UserTable.id,
                    UserPoolTable.pool_id == latest_pools.c.pool_id,
                ),
            )
            .where(UserTable.tg_id.is_not(None))
            .group_by(UserTable.id, UserTable.tg_id)
            .having(
                sa.and_(
                    sa.func.count(latest_pools.c.pool_id) == required_pools_count,
                    sa.func.count(UserPoolTable.pool_id) == 0,
                ),
            )
        )
        # fmt:on

        result = await self.session.execute(query)

        return cast(List[int], result.scalars().all())
