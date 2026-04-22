from pydantic import SecretStr

from src.schemas import DomainSettings


class AuthNav:
    LOGIN_PAGE = "login.html"
    REGISTER_PAGE = "register.html"
    DASHBOARD_PAGE = "dashboard.html"


class AuthSettings(DomainSettings):
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DEV_ROLE_KEYS: str = "{}"

# ----- DOMAIN INSTANCE
auth_settings = AuthSettings()
