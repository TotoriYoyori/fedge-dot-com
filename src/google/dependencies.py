from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.google.exceptions import (
    ExchangeCodeNotFound,
    StateNotFound,
)
from src.google.models import GoogleOAuthState
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
