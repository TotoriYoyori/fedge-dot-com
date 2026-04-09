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

    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Config()
