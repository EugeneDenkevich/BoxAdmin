from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message
from dishka.integrations.aiogram import FromDishka, inject

from app.domain.user.entities import User
from app.usecases.statistic import GetStatisticUseCase

router = Router(name=__name__)


@router.message(Command("statistic"))
@inject
async def handle_statistic(
    message: Message,
    *,
    user: FromDishka[User],
    get_statistic: FromDishka[GetStatisticUseCase],
) -> None:
    if not (user.is_staff or user.is_admin):
        await message.answer("Команда доступна только staff и admin.")

        return

    chart = await get_statistic()
    photo = BufferedInputFile(chart, filename="attendance.png")

    await message.answer_photo(
        photo=photo,
        caption="Посещаемость по голосованиям",
    )
