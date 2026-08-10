from aiogram import Router
from aiogram.types import PollAnswer
from loguru import logger

router = Router(name=__name__)


@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer) -> None:
    logger.info(
        "User voted for options: [USER_TG_ID: {}, OPRIONS: {}]",
        poll_answer.user.id if poll_answer.user else None,
        poll_answer.option_ids,
    )
