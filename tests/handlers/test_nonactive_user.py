from unittest.mock import AsyncMock

import pytest
from aiogram.types import CallbackQuery

from app.domain.user.entities import User
from app.handlers.telegram.nonactive_user import (
    NonactiveBanCallback,
    handle_nonactive_user_ban,
)
from app.services.user.service import UserService


def make_container(user: User, user_service: AsyncMock) -> AsyncMock:
    container = AsyncMock()
    container.get.side_effect = lambda dependency, _component: {
        User: user,
        UserService: user_service,
    }[dependency]

    return container


@pytest.mark.asyncio
async def test_staff_can_ban_currently_nonactive_user() -> None:
    callback_query = AsyncMock(spec=CallbackQuery)
    callback_query.answer = AsyncMock()
    callback_query.message = None
    user_service = AsyncMock(spec=UserService)
    user_service.get_user_by_tg_id.return_value = User(tg_id=456)
    user_service.is_nonactive_user.return_value = True
    user_service.ban_user.return_value = True

    await handle_nonactive_user_ban(
        callback_query,
        NonactiveBanCallback(tg_id=456),
        dishka_container=make_container(
            User(tg_id=101, is_staff=True),
            user_service,
        ),
    )

    user_service.ban_user.assert_awaited_once_with(456)
    callback_query.answer.assert_awaited_once_with("Пользователь забанен.")


@pytest.mark.asyncio
async def test_stale_card_does_not_ban_user() -> None:
    callback_query = AsyncMock(spec=CallbackQuery)
    callback_query.answer = AsyncMock()
    callback_query.message = None
    user_service = AsyncMock(spec=UserService)
    user_service.get_user_by_tg_id.return_value = User(tg_id=456)
    user_service.is_nonactive_user.return_value = False

    await handle_nonactive_user_ban(
        callback_query,
        NonactiveBanCallback(tg_id=456),
        dishka_container=make_container(
            User(tg_id=101, is_staff=True),
            user_service,
        ),
    )

    user_service.ban_user.assert_not_awaited()
    user_service.is_nonactive_user.assert_awaited_once_with(456)
    callback_query.answer.assert_awaited_once_with(
        "Карточка устарела: пользователь больше не подходит под критерий неактивности.",
        show_alert=True,
    )


@pytest.mark.asyncio
async def test_nonstaff_cannot_ban_user_from_callback() -> None:
    callback_query = AsyncMock(spec=CallbackQuery)
    callback_query.answer = AsyncMock()
    callback_query.message = None
    user_service = AsyncMock(spec=UserService)

    await handle_nonactive_user_ban(
        callback_query,
        NonactiveBanCallback(tg_id=456),
        dishka_container=make_container(
            User(tg_id=101, is_staff=False),
            user_service,
        ),
    )

    user_service.get_user_by_tg_id.assert_not_awaited()
    user_service.ban_user.assert_not_awaited()
    callback_query.answer.assert_awaited_once_with(
        "Недостаточно прав.",
        show_alert=True,
    )
