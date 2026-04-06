from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # --- Default, overridable with .env
    DATABASE_URL: str = ""
    ENVIRONMENT: str = ""
    APP_VERSION: str = ""
    ALLOW_ORIGINS: str = ""

    model_config = ConfigDict(env_file="../.env")


settings = Config()
