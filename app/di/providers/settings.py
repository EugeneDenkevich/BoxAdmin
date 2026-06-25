from dishka import Provider, from_context, Scope

from app.settings import Settings


class SettingsProvider(Provider):
    settings = from_context(Settings, scope=Scope.APP)
