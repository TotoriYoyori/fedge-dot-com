from datetime import datetime

from anyio import to_thread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.google.exceptions import ClientSecretNotFound, FaultyFlow, InvalidPKCE
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.settings import google_settings
from src.schemas import CustomBaseModel


# =============== CLIENT RECORD ===============
class GoogleOAuthCredentialRecord(CustomBaseModel):
    app_user_id: str
    access_token: str | None = None
    refresh_token: str | None = None
    token_uri: str
    client_id: str | None = None
    client_secret: str | None = None
    scopes: str
    expiry: datetime | None = None
    email_address: str | None = None


# =============== FLOW HELPERS ===============
def _generate_base_flow(state: str | None = None) -> Flow:
    try:
        return Flow.from_client_secrets_file(
            google_settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            state=state,
        )
    except FileNotFoundError:
        raise ClientSecretNotFound


def _attach_code_verifier(flow: Flow, code_verifier: str | None) -> Flow:
    if not code_verifier:
        raise InvalidPKCE

    flow.code_verifier = code_verifier
    return flow


# =============== OAUTH CLIENT ===============
def init_flow() -> tuple[str, str, str]:
    flow = _generate_base_flow()

    try:
        auth_url, state = flow.authorization_url(
            access_type=google_settings.FLOW_ACCESS_TYPE,
            include_granted_scopes=google_settings.FLOW_INCLUDE_GRANTED_SCOPES,
            prompt=google_settings.FLOW_PROMPT,
        )
    except Exception:
        raise FaultyFlow
    else:
        return auth_url, state, flow.code_verifier


async def pkce_flow(
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> Credentials:
    flow = _generate_base_flow(state=oauth_state.state)
    verified_flow = _attach_code_verifier(flow, oauth_state.code_verifier)

    try:
        verified_flow.fetch_token(code=exchange_code)
    except Exception:
        raise FaultyFlow

    return verified_flow.credentials


def build_app_oauth_credential(
    credentials: Credentials,
    app_user_id: str,
    email_address: str | None = None,
) -> GoogleOAuthCredentialRecord:
    return GoogleOAuthCredentialRecord(
        app_user_id=app_user_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri or "https://oauth2.googleapis.com/token",
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=",".join(credentials.scopes or []),
        expiry=credentials.expiry,
        email_address=email_address,
    )


def build_google_credentials(record: GoogleOAuthCredential) -> Credentials:
    return Credentials(
        token=record.access_token,
        refresh_token=record.refresh_token,
        token_uri=record.token_uri,
        client_id=record.client_id,
        client_secret=record.client_secret,
        scopes=record.scopes.split(","),
    )


async def refresh_credentials(credentials: Credentials) -> Credentials:
    await to_thread.run_sync(credentials.refresh, Request())
    return credentials


# =============== GMAIL CLIENT ===============
def create_gmail_service(record: GoogleOAuthCredential):
    creds = build_google_credentials(record)
    creds.expiry = record.expiry
    return create_gmail_service_from_credentials(creds)


def create_gmail_service_from_credentials(credentials: Credentials):
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


async def get_authorized_email(credentials: Credentials) -> str | None:
    service = create_gmail_service_from_credentials(credentials)
    profile = await to_thread.run_sync(
        lambda: service.users().getProfile(userId="me").execute()
    )
    return profile.get("emailAddress")
