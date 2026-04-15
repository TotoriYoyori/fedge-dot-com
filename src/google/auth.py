from google_auth_oauthlib.flow import Flow

from google.oauth2.credentials import Credentials
from src.google.config import (
    GOOGLE_CLIENT_SECRETS_FILE,
    GOOGLE_REDIRECT_URI,
    GOOGLE_SCOPES,
)


def get_google_flow(state: str = None) -> Flow:
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
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
