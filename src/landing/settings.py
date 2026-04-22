from src.schemas import DomainSettings


# ----- CONFIG
class LandingSettings(DomainSettings):
    # --- Template Navigation
    HOME_PAGE: str = "home.html"
    pass


# ----- DOMAIN INSTANCE
landing_settings = LandingSettings()
