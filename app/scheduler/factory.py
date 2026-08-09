from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.tasks import send_pool_task
from app.settings import Settings


def setup_scheduler(
    settings: Settings,
    bot: Bot,
) -> None:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    scheduler.start()

    scheduler.add_job(
        send_pool_task,
        "cron",
        hour=10,
        minute=00,
        day_of_week="0,2,4",
        kwargs={
            "bot": bot,
            "chat_id": settings.target_chat,
        },
    )
