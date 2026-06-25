from typing import Any, Dict, Optional, Tuple

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from app.di.providers.database import DatabaseProvider
from app.di.providers.repos import ReposProvider
from app.di.providers.service import ServicesProvider
from app.di.providers.settings import SettingsProvider
from app.di.providers.usecases import UseCaseProvider
from app.di.providers.user import UserProvider


def default_providers() -> Tuple[Provider, ...]:
    return (
        SettingsProvider(),
        DatabaseProvider(),
        ReposProvider(),
        ServicesProvider(),
        UseCaseProvider(),
        UserProvider(),
        AiogramProvider(),
    )


def get_di_container(
    *providers: Provider,
    context: Optional[Dict[Any, Any]] = None,
) -> AsyncContainer:
    return make_async_container(
        *providers,
        context=context,
    )
