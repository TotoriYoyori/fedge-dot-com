from anyio import to_thread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.auth.models import User
from src.google.exceptions import ClientSecretNotFound, FaultyFlow, InvalidPKCE
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.schemas import GoogleOAuth2CredentialCreate, GoogleOAuth2StateCreate
from src.google.settings import google_settings


# =============== FLOW HELPERS ===============
def _generate_base_flow(state: str | None = None) -> Flow:
    """Build a Google OAuth flow from the configured client secrets file.

    Args:
        state: Optional OAuth state to bind to the flow during callback exchange.

    Returns:
        Flow: Configured Google OAuth flow instance for authorization or token exchange.

    Raises:
        ClientSecretNotFound: If the configured Google client secrets file does not exist.

    Example:
        >>> flow = _generate_base_flow()
        >>> flow.redirect_uri
    """
    try:
        return Flow.from_client_secrets_file(
            google_settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
            state=state,
        )
    except FileNotFoundError:
        raise ClientSecretNotFound


def _attach_code_verifier(flow: Flow, code_verifier: str) -> Flow:
    if not code_verifier:
        raise InvalidPKCE

    flow.code_verifier = code_verifier
    return flow


# =============== FETCH STATE AND CREDENTIALS FROM GOOGLE SERVER ===============
def fetch_google_oauth_state(valid_user: User) -> GoogleOAuth2StateCreate:
    """Build and persist an OAuth authorization flow state.

    Args:
        valid_user: Authenticated application user starting the Google OAuth flow.

    Returns:
        GoogleOAuth2StateCreate: State payload containing the generated OAuth
        state, authorization URL, user id, and PKCE code verifier.

    Raises:
        FaultyFlow: If Google authorization URL generation fails.

    Example:
        >>> new_state = fetch_google_oauth_state(valid_user)
        >>> new_state.user_id
    """
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
        return GoogleOAuth2StateCreate(
            state=state,
            auth_url=auth_url,
            user_id=valid_user.id,
            code_verifier=flow.code_verifier,
        )


async def fetch_google_oauth_credential(
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuth2CredentialCreate:
    """Exchange a Google OAuth callback code for credential data using PKCE.

    Args:
        exchange_code: Authorization code returned by Google in the callback.
        oauth_state: Persisted OAuth state record containing the original state
            value, app user id, and PKCE code verifier.

    Returns:
        GoogleOAuth2CredentialCreate: Credential payload ready to be inserted or
        applied to an existing credential row.

    Raises:
        InvalidPKCE: If the persisted OAuth state does not contain a usable code
            verifier.
        FaultyFlow: If Google token exchange fails for any reason.

    Example:
        >>> async def run_example() -> int:
        ...     record = await fetch_google_oauth_credential(exchange_code, current_oauth_state)
        ...     return record.user_id
    """
    flow = _generate_base_flow(state=oauth_state.state)
    verified_flow = _attach_code_verifier(flow, oauth_state.code_verifier)

    try:
        verified_flow.fetch_token(code=exchange_code)
    except Exception:
        raise FaultyFlow

    credentials = verified_flow.credentials
    return GoogleOAuth2CredentialCreate(
        user_id=oauth_state.user_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri or "https://oauth2.googleapis.com/token",
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=",".join(credentials.scopes or []),
        expiry=credentials.expiry,
        email_address=None,
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
