from aiogram import Router
from aiogram.types import PollAnswer
from loguru import logger

from app.domain.user.entities import User
from app.services.pool.service import PoolService

router = Router(name=__name__)


@router.poll_answer()
async def handle_poll_answer(
    poll_answer: PollAnswer,
    user: User,
    pool_service: PoolService,
) -> None:
    logger.info(
        "User voted for options: [USER_TG_ID: {}, OPRIONS: {}]",
        poll_answer.user.id if poll_answer.user else None,
        poll_answer.option_ids,
    )

    await pool_service.save_vote(
        telegram_poll_id=poll_answer.poll_id,
        user_id=user.id,
        option_ids=poll_answer.option_ids,
    )
