from app.processors.statistic.protocol import StatisticProcessor
from app.services.pool.service import PoolService


class GetStatisticUseCase:
    def __init__(
        self,
        pool_service: PoolService,
        statistic_processor: StatisticProcessor,
    ) -> None:
        self.pool_service = pool_service
        self.statistic_processor = statistic_processor

    async def __call__(self) -> bytes:
        votes = await self.pool_service.get_attendance_votes()

        return self.statistic_processor.get_statistic(votes)
