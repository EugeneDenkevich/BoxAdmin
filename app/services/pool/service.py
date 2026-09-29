from typing import List
from uuid import UUID

from app.infra.uow import UoW
from app.repos.pool.repo import PoolRepo


class PoolService:
    def __init__(self, pool_repo: PoolRepo, uow: UoW) -> None:
        self.pool_repo = pool_repo
        self.uow = uow

    async def save_pool(self, telegram_poll_id: str) -> None:
        await self.pool_repo.save_pool(telegram_poll_id)
        await self.uow.commit()

    async def save_vote(
        self,
        telegram_poll_id: str,
        user_id: UUID,
        option_ids: List[int],
    ) -> None:
        pool = await self.pool_repo.get_pool(telegram_poll_id)

        await self.pool_repo.save_vote(pool.id, user_id, option_ids)
        await self.uow.commit()
