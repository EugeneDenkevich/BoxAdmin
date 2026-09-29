from aiogram import Router
from aiogram.types import PollAnswer
from dishka.integrations.aiogram import FromDishka, inject
from loguru import logger

from app.domain.pool.exceptions import PoolNotFoundError
from app.domain.user.entities import User
from app.services.pool.service import PoolService

router = Router(name=__name__)


@router.poll_answer()
@inject
async def handle_poll_answer(
    poll_answer: PollAnswer,
    *,
    user: FromDishka[User],
    pool_service: FromDishka[PoolService],
) -> None:
    logger.info(
        "User voted for options: [USER_TG_ID: {}, OPRIONS: {}]",
        poll_answer.user.id if poll_answer.user else None,
        poll_answer.option_ids,
    )

    try:
        await pool_service.save_vote(
            telegram_poll_id=poll_answer.poll_id,
            user_id=user.id,
            option_ids=poll_answer.option_ids,
        )
    except PoolNotFoundError:
        logger.warning("Ignoring vote for unknown poll: [TG_POOL_ID: {}]", poll_answer.poll_id)
