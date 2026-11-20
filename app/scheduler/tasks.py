from aiogram import Bot
from dishka import AsyncContainer, Scope

from app.services.pool.service import PoolService
from app.usecases.user.notify_nonactive_users import NotifyNonactiveUsersUseCasse


async def send_pool_task(
    bot: Bot,
    chat_id: int,
    container: AsyncContainer,
) -> None:
    message = await bot.send_poll(
        chat_id=chat_id,
        question="Кто планирует прийти сегодня? 🤔",
        options=["➕", "➖"],
        is_anonymous=False,
        allows_revoting=True,
        allows_multiple_answers=False,
        allow_adding_options=False,
        shuffle_options=False,
    )

    assert message.poll

    async with container(scope=Scope.REQUEST) as request_container:
        pool_service = await request_container.get(PoolService)

        await pool_service.save_pool(message.poll.id)


async def notify_nonactive_users_task(container: AsyncContainer) -> None:
    async with container(scope=Scope.REQUEST) as request_container:
        notify_nonactive_users = await request_container.get(NotifyNonactiveUsersUseCasse)

        await notify_nonactive_users()
