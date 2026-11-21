from dishka import Provider, Scope, provide

from app.processors.statistic.matplotlib.processor import MatplotlibProcessor
from app.processors.statistic.protocol import StatisticProcessor
from app.settings import Settings


class ProcessorProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_processor(self, settings: Settings) -> StatisticProcessor:
        return MatplotlibProcessor(timezone_name=settings.timezone)
