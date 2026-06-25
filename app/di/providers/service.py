from dishka import Provider, Scope, provide_all

from app.services import UserService


class ServicesProvider(Provider):
    all = provide_all(
        UserService,
        scope=Scope.REQUEST,
    )
