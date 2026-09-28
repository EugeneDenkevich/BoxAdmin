from dishka import Provider, Scope, provide_all

from app.services import PoolService, UserService


class ServicesProvider(Provider):
    all = provide_all(
        UserService,
        PoolService,
        scope=Scope.REQUEST,
    )
