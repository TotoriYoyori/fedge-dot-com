from fastapi.templating import Jinja2Templates

from src.schemas import DomainSettings

# ----- CONFIG
class LandingSettings(DomainSettings):
    # --- Template Navigation
    HOME_PAGE: str = "home.html"
    pass


# ----- DOMAIN INSTANCE
landing_settings = LandingSettings()
landing_page = Jinja2Templates(directory=landing_settings.TEMPLATES_DIR)
