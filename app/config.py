"""Settings management."""

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    auth_secret_key: str = ""
    auth_algorithm: str = "HS256"
    auth_token_expire_minutes: int = 60 # valid for 1 hour
    refresh_token_expire_minutes: int = 60 * 24 * 7  # valid for 1 week
    db_uri: str = ""


try:
    settings = Settings()
except ValidationError as e:
    print(f"Exception: {e}")  # TODO: replace with logger
