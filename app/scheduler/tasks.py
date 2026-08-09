from aiogram import Bot


async def send_pool_task(bot: Bot, chat_id: int) -> None:
    await bot.send_poll(
        chat_id=chat_id,
        question="Кто планирует прийти сегодня? 🤔",
        options=["➕", "➖"],
        is_anonymous=False,
        allows_revoting=True,
        allows_multiple_answers=False,
        allow_adding_options=False,
        shuffle_options=False,
    )
