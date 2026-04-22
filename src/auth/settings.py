from pydantic import SecretStr

from src.schemas import DomainSettings

# FIXME: Implement a navigating enum instead of coupling with AuthSettings
class AuthSettings(DomainSettings):
    LOGIN_PAGE: str = "login.html"
    REGISTER_PAGE: str = "register.html"
    DASHBOARD_PAGE: str = "dashboard.html" # FIXME: Must be moved to /users domain in the future.

    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DEV_ROLE_KEYS: str = "{}"

# ----- DOMAIN INSTANCE
auth_settings = AuthSettings()
