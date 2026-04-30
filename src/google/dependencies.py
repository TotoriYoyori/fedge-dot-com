from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.google.exceptions import (
    CredentialNotFound,
    ExchangeCodeNotFound,
    StateNotFound,
)
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.service import GoogleOAuthService


def valid_google_oauth2_exchange_code(
    exchange_code_query: Annotated[str | None, Query(alias="code")] = None
) -> str:
    if not exchange_code_query:
        raise ExchangeCodeNotFound

    return exchange_code_query


async def valid_google_oauth2_state(
    db: Annotated[AsyncSession, Depends(get_db)],
    state_query: Annotated[str | None, Query(alias="state")] = None
) -> GoogleOAuthState:
    if not state_query:
        raise StateNotFound

    oauth_state = await GoogleOAuthService.get_state(db, state_query)
    if oauth_state is None:
        raise StateNotFound

    return oauth_state


async def valid_google_oauth_credential(
    valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoogleOAuthCredential:
    record = await GoogleOAuthService.get_credential(db, str(valid_user.id))
    if record is None:
        raise CredentialNotFound

    return record
