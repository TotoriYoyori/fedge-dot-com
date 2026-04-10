from pydantic import ConfigDict, field_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # --- Default, overridable with .env
    DATABASE_URL: str = ""
    ENVIRONMENT: str = ""
    APP_VERSION: str = ""
    ALLOW_ORIGINS: str = ""

    # --- Authentication Layer
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Email Notification Layer
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "teainbasement@gmail.com"
    SMTP_PASSWORD: str = "jcws xtta hlqc mxwq"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Config()
