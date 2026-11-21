from unittest.mock import AsyncMock

import pytest
from aiogram.types import BufferedInputFile, Message

from app.domain.user.entities import User
from app.handlers.telegram.statistic import handle_statistic
from app.usecases.statistic import GetStatisticUseCase


def make_container(user: User, get_statistic: AsyncMock) -> AsyncMock:
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        User: user,
        GetStatisticUseCase: get_statistic,
    }[dependency]

    return container


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user",
    [User(is_staff=True), User(is_admin=True)],
    ids=["staff", "admin"],
)
async def test_staff_and_admin_receive_attendance_chart(user: User) -> None:
    message = AsyncMock(spec=Message)
    message.answer_photo = AsyncMock()
    get_statistic = AsyncMock()
    get_statistic.return_value = b"png-data"

    await handle_statistic(
        message,
        dishka_container=make_container(user, get_statistic),
    )

    get_statistic.assert_awaited_once_with()
    message.answer_photo.assert_awaited_once()
    photo = message.answer_photo.await_args.kwargs["photo"]
    assert isinstance(photo, BufferedInputFile)
    assert photo.filename == "attendance.png"
    assert message.answer_photo.await_args.kwargs["caption"] == (
        "Посещаемость по голосованиям"
    )


@pytest.mark.asyncio
async def test_other_users_cannot_access_attendance_chart() -> None:
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.answer_photo = AsyncMock()
    get_statistic = AsyncMock()
    user = User(is_staff=False, is_admin=False)

    await handle_statistic(
        message,
        dishka_container=make_container(user, get_statistic),
    )

    get_statistic.assert_not_awaited()
    message.answer_photo.assert_not_awaited()
    message.answer.assert_awaited_once_with(
        "Команда доступна только staff и admin.",
    )
