from pathlib import Path

from src.schemas import DomainSettings


# =============== DOMAIN SETTINGS ===============
class GoogleSettings(DomainSettings):
    """Domain settings for Google OAuth and Gmail integration."""

    # ----- Google OAuth General Settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/google/callback"
    GOOGLE_SCOPES: str = "openid,email,https://www.googleapis.com/auth/gmail.readonly"
    GOOGLE_CLIENT_SECRETS_FILE: str = ""

    # ----- Flow Generation Settings
    FLOW_ACCESS_TYPE: str = "offline"
    FLOW_INCLUDE_GRANTED_SCOPES: str = "true"
    FLOW_PROMPT: str = "consent"

    def model_post_init(self, __context):
        """
        Sets `GOOGLE_CLIENT_SECRETS_FILE` to the domain-local `credentials.json` file.

        Callers do not need to supply the path explicitly through environment configuration.
        """
        super().model_post_init(__context)
        object.__setattr__(
            self,
            "GOOGLE_CLIENT_SECRETS_FILE",
            str(Path(__file__).resolve().parent / "credentials.json"),
        )


# =============== SHARED SETTINGS ===============
google_settings = GoogleSettings()
