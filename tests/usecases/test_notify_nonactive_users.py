from unittest.mock import AsyncMock

import pytest

from app.usecases.user.notify_nonactive_users import NotifyNonactiveUsersUseCasse


@pytest.mark.asyncio
async def test_notifies_about_nonactive_users() -> None:
    user_service = AsyncMock()
    use_case = NotifyNonactiveUsersUseCasse(user_service=user_service)

    await use_case()

    user_service.notify_nonactive_users.assert_awaited_once()
