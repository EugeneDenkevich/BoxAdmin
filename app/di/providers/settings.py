from dishka import Provider, Scope, from_context

from app.settings import Settings


class SettingsProvider(Provider):
    settings = from_context(Settings, scope=Scope.APP)
