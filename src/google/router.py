from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.google.dependencies import (
    valid_google_oauth2_exchange_code,
    valid_google_oauth2_state,
    valid_google_oauth_credential,
)
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.service import (
    connect_gmail_service,
    initiate_oauth2,
    exchange_code_for_credentials,
    list_gmail_inbox,
)
from src.google.schemas import (
    GmailInboxResponse,
    GoogleOAuth2CredentialResponse,
    GoogleOAuth2RedirectResponse,
)


# =============== API ROUTER ===============
router = APIRouter(prefix="/api/v1/google", tags=["api-google"])


@router.post(
    "/oauth2",
    summary="Create Google OAuth2 authorization state",
    description=(
        "Creates a temporary OAuth2 state `new_state` for the authenticated user and "
        "returns the Google authorization URL (`auth_url`) the client should use to redirect "
        "the user."
    ),
    response_model=GoogleOAuth2RedirectResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "model": GoogleOAuth2RedirectResponse,
            "description": "Successfully created OAuth2 authorization state",
        },
        401: {"description": "Unauthorized access"},
        403: {"description": "Insufficient permissions"},
    },
)
async def oauth2(
    valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
    db: AsyncSession = Depends(get_db),
):
    return await initiate_oauth2(db, valid_user)


@router.get(
    "/callback",
    summary="Handle Google OAuth2 callback",
    description=(
        "Consumes the Google OAuth2 callback, validates the returned state, "
        "and exchanges the authorization code for Google OAuth2 credentials."
    ),
    response_model=GoogleOAuth2CredentialResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "model": GoogleOAuth2CredentialResponse,
            "description": "Successfully exchanged the callback code for credentials",
        },
        400: {"description": "Malformed callback or invalid state"},
    },
)
async def callback(
    exchange_code: Annotated[str, Depends(valid_google_oauth2_exchange_code)],
    oauth_state: Annotated[GoogleOAuthState, Depends(valid_google_oauth2_state)],
    db: AsyncSession = Depends(get_db),
):
    return await exchange_code_for_credentials(db, exchange_code, oauth_state)


@router.post(
    "/gmail",
    response_model=GoogleOAuth2CredentialResponse,
    status_code=status.HTTP_200_OK,
    summary="Connect Gmail service",
    description=(
        "Builds the Gmail service and syncs profile data using previously persisted "
        "Google OAuth2 credentials."
    ),
    responses={
        200: {
            "model": GoogleOAuth2CredentialResponse,
            "description": "Successfully synced Google OAuth2 credentials with Gmail",
        },
        404: {"description": "Google OAuth credential not found for app user"},
    },
)
async def gmail(
    record: Annotated[GoogleOAuthCredential, Depends(valid_google_oauth_credential)],
    db: AsyncSession = Depends(get_db),
):
    return await connect_gmail_service(db, record)


# =============== GMAIL ROUTES ===============
@router.get("/inbox", response_model=GmailInboxResponse)
async def list_inbox(
    record: Annotated[GoogleOAuthCredential, Depends(valid_google_oauth_credential)],
    max_results: int = Query(default=5, ge=1, le=100),
    sender: str | None = Query(default=None),
    label: str | None = Query(default=None),
    after: date | None = Query(default=None),
    before: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await list_gmail_inbox(
        db=db,
        record=record,
        max_results=max_results,
        sender=sender,
        label=label,
        after=after,
        before=before,
    )
