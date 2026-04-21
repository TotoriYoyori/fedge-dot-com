from pydantic import SecretStr, computed_field
from fastapi.templating import Jinja2Templates

from src.schemas import DomainSettings


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
auth_page = Jinja2Templates(directory=auth_settings.TEMPLATES_DIR)
