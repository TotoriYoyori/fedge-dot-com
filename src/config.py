import datetime as dt
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
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
    ENVIRONMENT: str
    ALLOW_ORIGINS: str

    # --- II.1 Authentication Layer
    SECRET_KEY: SecretStr
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- II.2 Email Notification Layer
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    # --- II.3 Google Authentication Layer
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_SCOPES: str

    # --- II.4 Roles Layer
    DEV_ROLE_KEYS: str

    # ----- III. Meta Configuration
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


@lru_cache
def get_settings():
    return Config()


settings = Config()
