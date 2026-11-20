from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NonactiveUserCandidate(BaseModel):
    user_id: UUID
    tg_id: int
    username: Optional[str] = None
    missed_pools_count: int
