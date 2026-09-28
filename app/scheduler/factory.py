import asyncio
from datetime import datetime

from aiogram import Bot
from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer

from app.error_reporter import ErrorReporter
from app.scheduler.tasks import ban_nonactive_users_task, send_pool_task
from app.settings import Settings


def get_scheduler(settings: Settings) -> AsyncIOScheduler:
    return AsyncIOScheduler(timezone=settings.timezone)


def setup_scheduler(
    scheduler: AsyncIOScheduler,
    target_chat: int,
    bot: Bot,
    reporter: ErrorReporter,
    container: AsyncContainer,
) -> AsyncIOScheduler:
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
    scheduler.add_job(
        send_pool_task,
        "cron",
        hour=10,
        minute=0,
        day_of_week="0,2,4",
        kwargs={
            "bot": bot,
            "chat_id": target_chat,
            "container": container,
        },
    )
    scheduler.add_job(
        ban_nonactive_users_task,
        "interval",
        hours=24,
        next_run_time=datetime.now(scheduler.timezone),
        id="ban_nonactive_users",
        kwargs={"container": container},
    )

    scheduler.start()

    return scheduler
