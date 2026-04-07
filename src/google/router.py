from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.google.auth import get_google_flow, fetch_credentials_from_code
from src.database import get_db
from src.google.schemas import GoogleCredentialResponse, GoogleInboxResponse
from src.google.service import (
    GoogleOAuthService,
    create_gmail_service,
    create_gmail_service_from_credentials,
    refresh_credential_if_needed,
)

router = APIRouter(prefix="/google", tags=["google"])

@router.get("/login")
async def login(
    app_user_id: str = Query(..., min_length=1, description="Your app's user identifier"),
    db: AsyncSession = Depends(get_db),
):
    flow = get_google_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    await GoogleOAuthService.create_state(
        db,
        state=state,
        app_user_id=app_user_id,
        code_verifier=flow.code_verifier,
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    oauth_state = await GoogleOAuthService.consume_state(db, state)
    if oauth_state is None:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    flow = get_google_flow(state=state)
    creds = fetch_credentials_from_code(
        flow,
        code,
        code_verifier=oauth_state.code_verifier,
    )
    gmail_service = create_gmail_service_from_credentials(creds)
    profile = gmail_service.users().getProfile(userId="me").execute()
    record = await GoogleOAuthService.upsert_credential(
        db,
        app_user_id=oauth_state.app_user_id,
        credentials=creds,
        email_address=profile.get("emailAddress"),
    )
    return {
        "message": "Google account connected",
        "credential": GoogleCredentialResponse(
            app_user_id=record.app_user_id,
            email_address=record.email_address,
            scopes=record.scopes.split(","),
            expiry=record.expiry,
        ),
        "next_steps": {
            "inbox": f"/google/inbox?app_user_id={oauth_state.app_user_id}",
        },
    }


@router.get("/credential", response_model=GoogleCredentialResponse)
async def get_credential(
    app_user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    record = await GoogleOAuthService.get_credential(db, app_user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Credential not found for app user")

    return GoogleCredentialResponse(
        app_user_id=record.app_user_id,
        email_address=record.email_address,
        scopes=record.scopes.split(","),
        expiry=record.expiry,
    )


@router.get("/inbox", response_model=GoogleInboxResponse)
async def list_inbox(
    app_user_id: str = Query(..., min_length=1),
    max_results: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    record = await GoogleOAuthService.get_credential(db, app_user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Credential not found for app user")

    record = await refresh_credential_if_needed(db, record)
    service = create_gmail_service(record)
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
    ).execute()
    return {
        "messages": results.get("messages", []),
        "resultSizeEstimate": results.get("resultSizeEstimate"),
    }
