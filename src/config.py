import datetime as dt
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# --------------- FASTAPI APP CONFIGURATION
class Config(BaseSettings):
    """
    Central configuration for the FastAPI application.

    Loads settings from environment variables and `.env`, including 1. database,
    2. JWT authentication, 3. email services, and 4. Google OAuth configs.

    Sensitive values should be stored securely in environment variables.
    """

    # ----- I. Default
    APP_NAME: str = "Fedge FastAPI Backend"
    LATEST_UPDATE: str = dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    APP_VERSION: str = "0.1"

    # ----- II. Environmental
    DATABASE_URL: str
    DB_ECHO: bool = True
    ENVIRONMENT: str = "local"
    ALLOW_ORIGINS: str = "*"

    # --- II.1 Authentication Layer
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # --- II.3 Roles Layer
    DEV_ROLE_KEYS: str = "{}"

    # ----- III. Paths
    @computed_field
    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @computed_field
    @property
    def notification_static_dir(self) -> Path:
        return self.project_root / "src" / "notification" / "static"

    # ----- IV. Meta Configuration
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


@lru_cache
def get_settings() -> Config:
    return Config()


settings = Config()
