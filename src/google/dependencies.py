from fastapi import Depends, Query
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.google.exceptions import (
    ExchangeCodeNotFound,
    FlowNotFound,
    StateNotFound,
)
from src.google.models import GoogleOAuthState
from src.google.schemas import GoogleOAuth2FlowContext
from src.google.service import GoogleOAuthService
from src.google.settings import google_settings


def _get_google_flow(state: str = None) -> Flow:
    return Flow.from_client_secrets_file(
        google_settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=google_settings.GOOGLE_SCOPES.split(","),
        redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
        state=state,
    )


def _fetch_credentials_from_code(
    flow: Flow,
    exchange_code: str,
    code_verifier: str | None = None,
) -> Credentials:
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(code=exchange_code)

    return flow.credentials


def generate_google_oauth2_flow() -> GoogleOAuth2FlowContext:
    try:
        flow = _get_google_flow()
    except Exception:
        raise FlowNotFound

    auth_url, state = flow.authorization_url(
        access_type=google_settings.FLOW_ACCESS_TYPE,
        include_granted_scopes=google_settings.FLOW_INCLUDE_GRANTED_SCOPES,
        prompt=google_settings.FLOW_PROMPT,
    )
    return GoogleOAuth2FlowContext(
        auth_url=auth_url,
        state=state,
        code_verifier=flow.code_verifier,
    )


def parse_google_oauth2_exchange_code(
    exchange_code: str | None = Query(default=None, alias="code"),
) -> str:
    if not exchange_code:
        raise ExchangeCodeNotFound

    return exchange_code


async def valid_google_oauth2_state(
    state: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> GoogleOAuthState:
    if not state:
        raise StateNotFound

    oauth_state = await GoogleOAuthService.consume_state(db, state)
    if oauth_state is None:
        raise StateNotFound

    return oauth_state
