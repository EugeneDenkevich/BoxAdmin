from dishka import Provider, provide_all, Scope

from app.services import UserService


class ServicesProvider(Provider):
    all = provide_all(
        UserService,
        scope=Scope.REQUEST,
    )
