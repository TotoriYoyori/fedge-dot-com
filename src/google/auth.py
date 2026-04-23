from google_auth_oauthlib.flow import Flow

from google.oauth2.credentials import Credentials
from src.google.settings import google_settings


def get_google_flow(state: str = None) -> Flow:
    if google_settings.GOOGLE_CLIENT_SECRETS_FILE:
        flow = Flow.from_client_secrets_file(
            google_settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            state=state,
        )
    else:
        client_config = {
            "web": {
                "client_id": google_settings.GOOGLE_CLIENT_ID,
                "client_secret": google_settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [google_settings.GOOGLE_REDIRECT_URI],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            state=state,
        )
    return flow


def fetch_credentials_from_code(
    flow: Flow,
    code: str,
    code_verifier: str | None = None,
) -> Credentials:
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(code=code)
    return flow.credentials
