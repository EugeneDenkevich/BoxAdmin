import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from app.domain.user.entities import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(CommandStart())
@inject
async def process_start(
    message: Message,
    state: FSMContext,
    user: FromDishka[User],
) -> None:
    if message.chat.type != "private":
        return

    await state.clear()

    username = f", *{user.username}*" if user.username else ""

    await message.answer(f"Hello{username}!\nYour telegram id is `{user.tg_id}`!")
