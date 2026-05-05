from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.google.exceptions import (
    CredentialNotFound,
    InvalidGoogleOAuthCallback,
)
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.service import get_oauth_credential, get_state, state_is_expired


# =============== CALLBACK CHECKS ===============
def valid_google_oauth2_exchange_code(
    exchange_code_in_query: Annotated[str | None, Query(alias="code")] = None,
) -> str:
    if not exchange_code_in_query:
        raise InvalidGoogleOAuthCallback

    return exchange_code_in_query


async def valid_google_oauth2_state(
    db: Annotated[AsyncSession, Depends(get_db)],
    state_in_query: Annotated[str | None, Query(alias="state")] = None,
) -> GoogleOAuthState:
    if not state_in_query:
        raise InvalidGoogleOAuthCallback

    oauth_state = await get_state(db, state_in_query)
    if oauth_state is None:
        raise InvalidGoogleOAuthCallback

    if state_is_expired(oauth_state):
        raise InvalidGoogleOAuthCallback

    return oauth_state

# =============== CREDENTIAL CHECKS ===============
async def valid_google_oauth_credential(
    valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoogleOAuthCredential:
    user_google_credential = await get_oauth_credential(db, valid_user.id)
    if user_google_credential is None:
        raise CredentialNotFound

    return user_google_credential
