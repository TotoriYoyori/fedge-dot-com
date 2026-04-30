from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.google.dependencies import (
    valid_google_oauth2_exchange_code,
    valid_google_oauth2_state,
)
from src.google.models import GoogleOAuthState
from src.google.schemas import (
    GoogleOAuth2CredentialResponse,
    GoogleInboxResponse,
    GoogleOAuth2RedirectResponse,
)

from src.google.service import (
    exchange_code_for_credentials,
    initiate_oauth2,
)

# --------------- API GOOGLE OAUTH ROUTER
router = APIRouter(prefix="/api/v1/google", tags=["api-google"])


@router.post(
    "/oauth2",
    summary="Create Google OAuth2 authorization state",
    description=(
        "Creates a temporary OAuth2 state record for the authenticated user and "
        "returns the Google authorization URL the client should use to redirect "
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


@router.get(
    "/callback/profile",
    summary="Handle deferred Google profile work",
    description=(
        "Placeholder route for the Gmail service and profile lookup work that "
        "used to live in the OAuth2 callback."
    ),
    status_code=status.HTTP_200_OK,
)
async def callback_profile(
    exchange_code: Annotated[str, Depends(valid_google_oauth2_exchange_code)],
    oauth_state: Annotated[GoogleOAuthState, Depends(valid_google_oauth2_state)],
    db: AsyncSession = Depends(get_db),
):
    # creds = await exchange_code_for_credentials(
    #     db=db,
    #     exchange_code=exchange_code,
    #     oauth_state=oauth_state,
    # )
    # gmail_service = GoogleOAuthSecurity.create_gmail_service_from_credentials(creds)
    # profile = gmail_service.users().getProfile(userId="me").execute()
    # record = await GoogleOAuthService.upsert_credential(
    #     db,
    #     app_user_id=oauth_state.app_user_id,
    #     credentials=creds,
    #     email_address=profile.get("emailAddress"),
    # )
    # return GoogleCredentialResponse(
    #     app_user_id=record.app_user_id,
    #     email_address=record.email_address,
    #     scopes=record.scopes.split(","),
    #     expiry=record.expiry,
    # )
    pass


@router.get("/me", response_model=GoogleOAuth2CredentialResponse)
async def me(
    app_user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    pass
    # record = await GoogleOAuthService.get_credential(db, app_user_id)
    # if record is None:
    #     raise HTTPException(status_code=404, detail="Credential not found for app user")
    #
    # return GoogleCredentialResponse(
    #     app_user_id=record.app_user_id,
    #     email_address=record.email_address,
    #     scopes=record.scopes.split(","),
    #     expiry=record.expiry,
    # )


@router.get("/inbox", response_model=GoogleInboxResponse)
async def list_inbox(
    app_user_id: str = Query(..., min_length=1),
    max_results: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    pass
    # record = await GoogleOAuthService.get_credential(db, app_user_id)
    # if record is None:
    #     raise HTTPException(status_code=404, detail="Credential not found for app user")
    #
    # record = await refresh_credential_if_needed(db, record)
    # service = GoogleOAuthSecurity.create_gmail_service(record)
    # results = (
    #     service.users()
    #     .messages()
    #     .list(
    #         userId="me",
    #         maxResults=max_results,
    #     )
    #     .execute()
    # )
    # return {
    #     "messages": results.get("messages", []),
    #     "resultSizeEstimate": results.get("resultSizeEstimate"),
    # }
