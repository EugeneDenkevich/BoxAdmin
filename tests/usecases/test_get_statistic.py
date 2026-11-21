from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.processors.statistic.protocol import StatisticProcessor
from app.schemas import PoolAttendanceVote
from app.services.pool.service import PoolService
from app.usecases.statistic import GetStatisticUseCase


@pytest.mark.asyncio
async def test_get_statistic_fetches_votes_and_processes_them() -> None:
    votes = [
        PoolAttendanceVote(
            pool_id=uuid4(),
            created_at=datetime(2026, 1, 1, 10, tzinfo=timezone.utc),
            option_ids=[0],
        ),
    ]
    pool_service = AsyncMock(spec=PoolService)
    pool_service.get_attendance_votes.return_value = votes
    processor = Mock(spec=StatisticProcessor)
    processor.get_statistic.return_value = b"chart"
    use_case = GetStatisticUseCase(pool_service, processor)

    result = await use_case()

    assert result == b"chart"
    pool_service.get_attendance_votes.assert_awaited_once_with()
    processor.get_statistic.assert_called_once_with(votes)
