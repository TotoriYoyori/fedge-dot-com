from fastapi.templating import Jinja2Templates

from src.schemas import DomainSettings


class AuthSettings(DomainSettings):
    pass

# ----- DOMAIN INSTANCE
auth_settings = AuthSettings()
auth_renderer = Jinja2Templates(directory=auth_settings.TEMPLATES_DIR)
