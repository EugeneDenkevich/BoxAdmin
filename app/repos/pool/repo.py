from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as psql_insert

from app.domain.pool.entities import Pool
from app.domain.pool.exceptions import PoolNotFoundError
from app.infra.db.tables.pool import PoolTable, UserPoolTable
from app.repos.base import BaseRepo
from app.repos.pool.converters import pool_db_to_entity


class PoolRepo(BaseRepo):
    async def save_pool(self, telegram_poll_id: str) -> None:
        self.session.add(PoolTable(telegram_poll_id=telegram_poll_id))
        await self.session.flush()

    async def get_pool_or_none(self, telegram_poll_id: str) -> Optional[Pool]:
        # fmt: off
        query = (
            sa
            .select(PoolTable)
            .where(PoolTable.telegram_poll_id == telegram_poll_id)
        )
        # fmt: on

        pool = await self._get_or_none(query)

        return pool_db_to_entity(pool) if pool else None

    async def get_pool(self, telegram_poll_id: str) -> Pool:
        pool = await self.get_pool_or_none(telegram_poll_id)

        if pool is None:
            raise PoolNotFoundError()

        return pool

    async def save_vote(
        self,
        pool_id: UUID,
        user_id: UUID,
        option_ids: List[int],
    ) -> None:
        # fmt: off
        stmt = (
            psql_insert(UserPoolTable)
            .values(
                user_id=user_id,
                pool_id=pool_id,
                option_ids=option_ids,
            )
            .on_conflict_do_update(
                index_elements=[UserPoolTable.user_id, UserPoolTable.pool_id],
                set_={
                    "option_ids": option_ids,
                    "updated_at": sa.func.now(),
                },
            )
        )
        # fmt: on

        await self.session.execute(stmt)
