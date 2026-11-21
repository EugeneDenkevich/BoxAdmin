from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from matplotlib.axes import Axes

from app.processors.statistic.matplotlib.processor import MatplotlibProcessor
from app.schemas import PoolAttendanceVote


def test_processor_counts_attending_votes_and_converts_timezone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processor = MatplotlibProcessor(timezone_name="Europe/Moscow")
    first_pool_id = uuid4()
    second_pool_id = uuid4()
    first_pool_created_at = datetime(2026, 1, 1, 22, 30, tzinfo=timezone.utc)
    second_pool_created_at = datetime(2026, 1, 3, 10, tzinfo=timezone.utc)
    captured_attendance: list[tuple[datetime, int]] = []

    def capture_attendance(
        _axis: Axes,
        attendance: list[tuple[datetime, int]],
    ) -> None:
        captured_attendance.extend(attendance)

    monkeypatch.setattr(processor, "_draw_attendance", capture_attendance)

    result = processor.get_statistic(
        [
            PoolAttendanceVote(
                pool_id=first_pool_id,
                created_at=first_pool_created_at,
                option_ids=[0],
            ),
            PoolAttendanceVote(
                pool_id=first_pool_id,
                created_at=first_pool_created_at,
                option_ids=[1],
            ),
            PoolAttendanceVote(
                pool_id=first_pool_id,
                created_at=first_pool_created_at,
                option_ids=[],
            ),
            PoolAttendanceVote(
                pool_id=second_pool_id,
                created_at=second_pool_created_at,
                option_ids=None,
            ),
        ],
    )

    assert result.startswith(b"\x89PNG\r\n\x1a\n")
    assert captured_attendance == [
        (datetime(2026, 1, 2, 1, 30, tzinfo=ZoneInfo("Europe/Moscow")), 1),
        (datetime(2026, 1, 3, 13, tzinfo=ZoneInfo("Europe/Moscow")), 0),
    ]


def test_processor_limits_chart_to_last_twenty_pools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processor = MatplotlibProcessor(timezone_name="UTC")
    captured_attendance: list[tuple[datetime, int]] = []

    def capture_attendance(
        _axis: Axes,
        attendance: list[tuple[datetime, int]],
    ) -> None:
        captured_attendance.extend(attendance)

    monkeypatch.setattr(processor, "_draw_attendance", capture_attendance)
    votes = [
        PoolAttendanceVote(
            pool_id=uuid4(),
            created_at=datetime(2026, 1, day, tzinfo=timezone.utc),
            option_ids=[0],
        )
        for day in range(1, 22)
    ]

    processor.get_statistic(votes)

    assert len(captured_attendance) == 20
    assert captured_attendance[0] == (
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        1,
    )
    assert captured_attendance[-1] == (
        datetime(2026, 1, 21, tzinfo=timezone.utc),
        1,
    )


def test_processor_returns_png_when_there_are_no_pools() -> None:
    processor = MatplotlibProcessor(timezone_name="UTC")

    result = processor.get_statistic([])

    assert result.startswith(b"\x89PNG\r\n\x1a\n")


def test_processor_renders_attendance_chart_for_votes() -> None:
    processor = MatplotlibProcessor(timezone_name="UTC")
    pool_id = uuid4()
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    votes = [
        PoolAttendanceVote(
            pool_id=pool_id,
            created_at=created_at,
            option_ids=[0],
        ),
        PoolAttendanceVote(
            pool_id=pool_id,
            created_at=created_at,
            option_ids=[1],
        ),
    ]

    result = processor.get_statistic(votes)

    assert result.startswith(b"\x89PNG\r\n\x1a\n")
