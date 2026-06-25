from typing import Optional

from app.domain.base import Entity


class User(Entity):
    tg_id: Optional[int] = None
    username: Optional[str] = None
    is_admin: bool = False
