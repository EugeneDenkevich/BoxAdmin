from typing import List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.repos.base import BaseRepo


class PoolRepo(BaseRepo):
    async def save_pool(self, telegram_poll_id: str) -> None:
        self.session.add(PoolTable(telegram_poll_id=telegram_poll_id))
        await self.session.flush()

    async def save_vote(
        self,
        telegram_poll_id: str,
        user_id: UUID,
        option_ids: List[int],
    ) -> bool:
        pool = await self._get_or_none(
            sa.select(PoolTable).where(PoolTable.telegram_poll_id == telegram_poll_id),
        )

        if pool is None:
            return False

        if not option_ids:
            await self.session.execute(
                sa.delete(UserPoolTable).where(
                    UserPoolTable.user_id == user_id,
                    UserPoolTable.pool_id == pool.id,
                ),
            )
        else:
            statement = insert(UserPoolTable).values(
                user_id=user_id,
                pool_id=pool.id,
                option_ids=option_ids,
            )
            statement = statement.on_conflict_do_update(
                index_elements=[UserPoolTable.user_id, UserPoolTable.pool_id],
                set_={
                    "option_ids": option_ids,
                    "updated_at": sa.func.now(),
                },
            )
            await self.session.execute(statement)

        await self.session.flush()
        return True
