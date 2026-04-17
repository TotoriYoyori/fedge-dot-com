from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/google/callback"
    GOOGLE_SCOPES: str = "openid,email,https://www.googleapis.com/auth/gmail.readonly"
    GOOGLE_CLIENT_SECRETS_FILE: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


google_settings = GoogleSettings()
