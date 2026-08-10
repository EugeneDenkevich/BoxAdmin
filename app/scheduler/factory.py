import asyncio

from aiogram import Bot
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.error_reporter import ErrorReporter
from app.scheduler.tasks import send_pool_task
from app.settings import Settings


def setup_scheduler(
    settings: Settings,
    bot: Bot,
    reporter: ErrorReporter,
) -> None:
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    def on_job_error(event: JobExecutionEvent) -> None:
        if event.exception is None:
            return

        asyncio.create_task(
            reporter.report(
                event.exception,
                context=f"scheduler job_id={event.job_id}",
            ),
        )

    scheduler.add_listener(on_job_error, EVENT_JOB_ERROR)
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
