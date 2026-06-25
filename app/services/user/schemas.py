from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UpdateUserData(BaseModel):
    user_id: UUID
    tg_id: Optional[int] = None
    username: Optional[str] = None
    is_admin: Optional[bool] = None
