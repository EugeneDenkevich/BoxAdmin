from dishka import Provider, Scope, provide_all

from app.usecases.user import (
    GetOrCreateTgUserUseCase,
    GetUserOrNoneUseCase,
    NotifyNonactiveUsersUseCasse,
    UpdateUserUseCase,
)


class UseCaseProvider(Provider):
    all = provide_all(
        GetUserOrNoneUseCase,
        GetOrCreateTgUserUseCase,
        UpdateUserUseCase,
        NotifyNonactiveUsersUseCasse,
        scope=Scope.REQUEST,
    )
