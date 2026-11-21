from typing import Protocol, Sequence

from app.schemas import PoolAttendanceVote


class StatisticProcessor(Protocol):
    def get_statistic(self, votes: Sequence[PoolAttendanceVote]) -> bytes: ...
