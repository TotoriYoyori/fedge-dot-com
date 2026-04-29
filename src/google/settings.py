from src.schemas import DomainSettings


class GoogleSettings(DomainSettings):
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/google/callback"
    GOOGLE_SCOPES: str = "openid,email,https://www.googleapis.com/auth/gmail.readonly"
    GOOGLE_CLIENT_SECRETS_FILE: str | None = None

    # ----- Flow Generation Settings
    FLOW_ACCESS_TYPE: str = "offline"
    FLOW_INCLUDE_GRANTED_SCOPES: str = "true"
    FLOW_PROMPT: str = "consent"


google_settings = GoogleSettings()
