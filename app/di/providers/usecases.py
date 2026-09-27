from dishka import Provider, Scope, provide_all

from app.usecases.user import (
    BanNonactiveUsers,
    GetOrCreateTgUserUseCase,
    GetUserOrNoneUseCase,
    UpdateUserUseCase,
)


class UseCaseProvider(Provider):
    all = provide_all(
        GetUserOrNoneUseCase,
        GetOrCreateTgUserUseCase,
        UpdateUserUseCase,
        BanNonactiveUsers,
        scope=Scope.REQUEST,
    )
