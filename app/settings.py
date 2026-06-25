from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class BaseConfig(BaseSettings):
    """Base configuration for app"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP__",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseConfig):
    """Settings for app"""

    dev_mode: bool = False

    bot_token: str = ""

    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "box_bot_manager"
    db_pass: str = "box_bot_manager"
    db_name: str = "box_bot_manager"

    def get_db_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            username=self.db_user,
            password=self.db_pass,
            database=self.db_name,
        )


def get_settings() -> Settings:
    """Get Settings for app"""

    return Settings()
