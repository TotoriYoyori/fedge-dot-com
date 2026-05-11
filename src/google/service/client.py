from datetime import UTC, datetime, timedelta

import asyncer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pydantic import ValidationError

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
    """Build a base Google OAuth flow from env config or the client secrets file.

    Returns:
        Flow: Configured Google OAuth flow instance without a callback state attached.

    Raises:
        ClientSecretNotFound: If neither env client config nor the secrets file is available.

    Example:
        >>> flow = _fetch_base_flow()
        >>> flow.redirect_uri
    """
    if google_settings.has_env_client_config:
        return Flow.from_client_config(
            google_settings.oauth_client_config(),
            scopes=google_settings.GOOGLE_SCOPES.split(","),
            redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
        )

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


def _convert_credential(user_google_credential: GoogleOAuthCredential) -> Credentials:
    """Convert an app-layer OAuth user_google_credential into Google's SDK primitive.

    Args:
        user_google_credential: Persisted application user_google_credential user_google_credential containing Google OAuth fields.

    Returns:
        Credentials: Google new_credential built from the stored application user_google_credential.

    Example:
        >>> new_credential = _convert_credential(user_google_credential)
        >>> new_credential.token
    """
    credentials = Credentials(
        token=user_google_credential.access_token,
        refresh_token=user_google_credential.refresh_token,
        token_uri=user_google_credential.token_uri,
        client_id=user_google_credential.client_id,
        client_secret=user_google_credential.client_secret,
        scopes=user_google_credential.scopes.split(","),
    )
    expiry = user_google_credential.expiry

    if expiry is not None and expiry.tzinfo is not None:
        expiry = expiry.astimezone(UTC).replace(tzinfo=None)

    credentials.expiry = expiry

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
        new_state = GoogleOAuth2StateCreate(
            state=state,
            auth_url=auth_url,
            user_id=valid_user.id,
            code_verifier=flow.code_verifier,
        )
    except ValidationError:
        raise FaultyFlow
    else:
        return new_state


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
    """Exchange a Google OAuth callback code for user_google_credential data using PKCE.

    Args:
        exchange_code: Authorization code returned by Google in the callback.
        oauth_state: Persisted OAuth state user_google_credential containing the original state
            value, app user id, and PKCE code verifier.

    Returns:
        GoogleOAuth2CredentialCreate: Credential payload ready to be inserted or
        applied to an existing user_google_credential row.

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
    verified_flow.fetch_token(code=exchange_code)

    credentials = verified_flow.credentials
    try:
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
    except ValidationError:
        raise FaultyFlow


async def fetch_refreshed_google_oauth_credential(
    user_google_credential: GoogleOAuthCredential,
) -> GoogleOAuth2CredentialCreate | None:
    credentials = _convert_credential(user_google_credential)
    if not credentials.expired:
        return None

    await asyncer.asyncify(credentials.refresh)(Request())

    return GoogleOAuth2CredentialCreate(
        user_id=user_google_credential.user_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token
            or user_google_credential.refresh_token,
        token_uri=credentials.token_uri or user_google_credential.token_uri,
        client_id=credentials.client_id or user_google_credential.client_id,
        client_secret=credentials.client_secret
            or user_google_credential.client_secret,
        scopes=",".join(credentials.scopes or []) or user_google_credential.scopes,
        expiry=credentials.expiry,
        email_address=user_google_credential.email_address,
    )


async def credential_is_stale(
    user_google_credential: GoogleOAuthCredential,
) -> bool:
    """Return whether a stored Google OAuth user_google_credential is expired and not refreshable.

    Args:
        user_google_credential: Persisted application user_google_credential user_google_credential containing Google OAuth fields.

    Returns:
        bool: ``True`` when the user_google_credential is expired and has no refresh token.

    Example:
        >>> async def run_example() -> bool:
        ...     return await credential_is_stale(user_google_credential)
    """
    credentials = _convert_credential(user_google_credential)

    return bool(credentials.expired and not credentials.refresh_token)


# =============== GMAIL CLIENT ===============
def get_gmail_service(user_google_credential: GoogleOAuthCredential):
    creds = _convert_credential(user_google_credential)

    return build("gmail","v1", credentials=creds, cache_discovery=False)
