from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NonactiveUserCandidate(BaseModel):
    user_id: UUID
    tg_id: int
    username: Optional[str] = None
    missed_pools_count: int


class InlineKeyboardButtonSchema(BaseModel):
    text: str
    callback_data: str


class InlineKeyboardMarkupSchema(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButtonSchema]]
