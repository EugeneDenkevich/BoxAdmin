from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from loguru import logger

from app.domain.user.entities import User
from app.services.user.service import UserService

router = Router(name=__name__)


class NonactiveBanCallback(CallbackData, prefix="nonactive_ban"):
    tg_id: int


@router.callback_query(NonactiveBanCallback.filter())
@inject
async def handle_nonactive_user_ban(
    callback_query: CallbackQuery,
    callback_data: NonactiveBanCallback,
    *,
    user: FromDishka[User],
    user_service: FromDishka[UserService],
) -> None:
    if not user.is_staff:
        await callback_query.answer("Недостаточно прав.", show_alert=True)

        return

    target_user = await user_service.get_user_by_tg_id(callback_data.tg_id)

    if target_user.is_banned:
        await callback_query.answer("Пользователь уже забанен.", show_alert=True)
        await _remove_button(callback_query)

        return

    if target_user.is_admin or target_user.is_staff:
        await callback_query.answer(
            "Пользователь имеет защищенный статус и не может быть забанен.",
            show_alert=True,
        )
        await _remove_button(callback_query)

        return

    if not await user_service.is_nonactive_user(callback_data.tg_id):
        await callback_query.answer(
            "Карточка устарела: пользователь больше не подходит под критерий неактивности.",
            show_alert=True,
        )
        await _remove_button(callback_query)

        return

    is_banned = await user_service.ban_user(callback_data.tg_id)

    if is_banned:
        await callback_query.answer("Пользователь забанен.")
    else:
        await callback_query.answer(
            "Бан не выполнен: пользователь уже забанен или имеет защищенный статус.",
            show_alert=True,
        )

    await _remove_button(callback_query)


async def _remove_button(callback_query: CallbackQuery) -> None:
    if not isinstance(callback_query.message, Message):
        return

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except TelegramAPIError:
        logger.exception("Failed to remove nonactive user ban button")
