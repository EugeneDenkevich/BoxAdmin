from dishka import Provider, Scope, WithParents, provide

from app.repos.user.repo import UserRepo


class ReposProvider(Provider):
    scope = Scope.REQUEST

    user_repo = provide(UserRepo, provides=WithParents[UserRepo])
