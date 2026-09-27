from dishka import Provider, Scope, WithParents, provide

from app.repos.pool.repo import PoolRepo
from app.repos.user.repo import UserRepo


class ReposProvider(Provider):
    scope = Scope.REQUEST

    user_repo = provide(UserRepo, provides=WithParents[UserRepo])
    pool_repo = provide(PoolRepo, provides=WithParents[PoolRepo])
