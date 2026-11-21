from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from app.domain.user.entities import User

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
    response = f"Hello{username}!\nYour telegram id is `{user.tg_id}`!"

    if user.is_staff or user.is_admin:
        instructions = [
            "*Команды:*",
            "`/start` — показать ваш Telegram ID.",
        ]

        if user.is_staff:
            instructions.append(
                "*Staff:* получайте уведомления о "
                "неактивных пользователях. Для бана "
                "нажмите «Забанить» в уведомлении.",
            )

        if user.is_admin:
            admin_instruction = (
                "*Admin:* отдельных команд нет; аккаунт "
                "защищён от бана."
            )

            if not user.is_staff:
                admin_instruction += (
                    " Для уведомлений и использования "
                    "кнопки также нужна роль staff."
                )

            instructions.append(admin_instruction)

        response += "\n\n" + "\n".join(instructions)

    await message.answer(response)
