from collections.abc import AsyncIterator

from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infra.uow import UoW
from app.settings import Settings


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_async_engine(
        self,
        settings: Settings,
    ) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            make_url(settings.get_db_url()),
            pool_size=10,
            max_overflow=10,
            pool_timeout=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        yield engine

        await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker[AsyncSession](
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_async_session(
        self,
        pool: async_sessionmaker[AsyncSession],
    ) -> AsyncIterator[AnyOf[AsyncSession, UoW]]:
        async with pool() as session:
            yield session
