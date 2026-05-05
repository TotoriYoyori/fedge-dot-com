from datetime import UTC, datetime, timedelta

import asyncer
from anyio import to_thread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.auth.models import User
from src.google.exceptions import (
    ClientSecretNotFound,
    FaultyFlow,
    InvalidPKCE,
)
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.schemas import GoogleOAuth2CredentialCreate, GoogleOAuth2StateCreate
from src.google.settings import google_settings


# =============== FLOW HELPERS ===============
def _fetch_base_flow() -> Flow:
    """Build a base Google OAuth flow from the configured client secrets file.

    Returns:
        Flow: Configured Google OAuth flow instance without callback state attached.

    Raises:
        ClientSecretNotFound: If the configured Google client secrets file does not exist.

    Example:
        >>> flow = _fetch_base_flow()
        >>> flow.redirect_uri
    """
    try:
        return Flow.from_client_secrets_file(
            google_settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
        )
    except FileNotFoundError:
        raise ClientSecretNotFound


def _attach_pkce(flow: Flow, state: str, code_verifier: str) -> Flow:
    """Attach OAuth callback state and PKCE verifier to a Google OAuth flow.

    Args:
        flow: OAuth flow instance that will use the state and verifier during token
            exchange.
        state: Persisted OAuth state value that scopes the token exchange.
        code_verifier: PKCE code verifier previously generated for the flow.

    Returns:
        Flow: The same OAuth flow instance with its state and code verifier attached.

    Raises:
        InvalidPKCE: If the provided code verifier is empty or missing.

    Example:
        >>> sample_flow = _fetch_base_flow()
        >>> verified_flow = _attach_pkce(sample_flow, "state", "verifier")
        >>> verified_flow.state
        >>> verified_flow.code_verifier
    """
    if not code_verifier:
        raise InvalidPKCE

    flow.state = state
    flow.code_verifier = code_verifier
    return flow


def _convert_credential(record: GoogleOAuthCredential) -> Credentials:
    """Convert an app-layer OAuth credential record into Google credentials.

    Args:
        record: Persisted application credential record containing Google OAuth fields.

    Returns:
        Credentials: Google credentials built from the stored application record.

    Example:
        >>> credentials = _convert_credential(record)
        >>> credentials.token
    """
    credentials = Credentials(
        token=record.access_token,
        refresh_token=record.refresh_token,
        token_uri=record.token_uri,
        client_id=record.client_id,
        client_secret=record.client_secret,
        scopes=record.scopes.split(","),
    )
    credentials.expiry = record.expiry
    return credentials


# =============== FETCH STATE FROM GOOGLE SERVER ===============
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
    flow = _fetch_base_flow()

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


def state_is_stale(oauth_state: GoogleOAuthState) -> bool:
    expires_at = oauth_state.created_time + timedelta(
        minutes=google_settings.FLOW_STATE_TTL_MINUTES
    )
    return expires_at <= datetime.now(UTC)


# =============== FETCH CREDENTIALS FROM GOOGLE SERVER ===============
async def fetch_google_oauth_credential(
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuth2CredentialCreate:
    """Exchange a Google OAuth callback code for credential data using PKCE.

    Args:
        exchange_code: Authorization code returned by Google in the callback.
        oauth_state: Persisted OAuth state user_google_credential containing the original state
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
        ...     user_google_credential = await fetch_google_oauth_credential(exchange_code, current_oauth_state)
        ...     return user_google_credential.user_id
    """
    flow = _fetch_base_flow()
    verified_flow = _attach_pkce(flow, oauth_state.state, oauth_state.code_verifier)

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


async def refresh_google_oauth_credential(credentials: Credentials) -> Credentials:
    await asyncer.asyncify(credentials.refresh)(Request())

    return credentials


async def credential_is_stale(
    record: GoogleOAuthCredential,
) -> bool:
    """Return whether a stored Google OAuth credential is expired and not refreshable.

    Args:
        record: Persisted application credential record containing Google OAuth fields.

    Returns:
        bool: ``True`` when the credential is expired and has no refresh token.

    Example:
        >>> async def run_example() -> bool:
        ...     return await credential_is_stale(record)
    """
    credentials = _convert_credential(record)
    return bool(credentials.expired and not credentials.refresh_token)


# =============== GMAIL CLIENT ===============
def create_gmail_service(record: GoogleOAuthCredential):
    creds = _convert_credential(record)
    return create_gmail_service_from_credentials(creds)


def create_gmail_service_from_credentials(credentials: Credentials):
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


async def get_authorized_email(credentials: Credentials) -> str | None:
    service = create_gmail_service_from_credentials(credentials)
    profile = await to_thread.run_sync(
        lambda: service.users().getProfile(userId="me").execute()
    )
    return profile.get("emailAddress")
