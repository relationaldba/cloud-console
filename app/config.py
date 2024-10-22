"""Settings management."""

from datetime import date
from logging import config

from pydantic import PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings class for application settings.

    This class loads the settings from environment variables or a `.env` file.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    auth_secret_key: str = ""
    auth_algorithm: str = "HS256"
    auth_token_expire_minutes: int = 60
    remember_me_minutes: int = 60 * 24  # valid for 1 day
    refresh_token_expire_minutes: int | None = 60
    db_uri: PostgresDsn | None = None


class Configuration(BaseSettings):
    """
    Settings class for application config like Organization name, address, etc.
    This class loads the settings from environment variables or a `.env` file.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    current_date: date = date.today()
    organization_name: str = "ACME Corp"
    organization_short_name: str = "ACME"
    organization_address: str = "123 Main St Acme City, USA 12345"
    organization_email: str = "noreply@acme.com"
    organization_phone: str = "+1234567890"


try:
    settings = Settings()
    config = Configuration()

except ValidationError as e:
    print(f"Exception: {e}")  # TODO: replace with logger
