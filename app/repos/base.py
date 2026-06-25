from typing import Optional, Tuple, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.base import BaseTable

T = TypeVar("T", bound=BaseTable)


class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_or_none(
        self,
        query: sa.Select[Tuple[T]],
    ) -> Optional[T]:
        result = await self.session.execute(query)

        return result.scalar()
