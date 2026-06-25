from dishka import Provider, provide_all, Scope

from app.usecases.user import (
    GetOrCreateTgUserUseCase,
    GetUserOrNoneUseCase,
    UpdateUserUseCase,
)


class UseCaseProvider(Provider):
    all = provide_all(
        GetUserOrNoneUseCase,
        GetOrCreateTgUserUseCase,
        UpdateUserUseCase,
        scope=Scope.REQUEST,
    )
