from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.schemas import (
    GoogleOAuth2CredentialResponse,
    GoogleOAuth2RedirectResponse,
)

from src.google.service.client import (
    build_app_oauth_credential,
    build_google_credentials,
    get_authorized_email,
    init_flow,
    pkce_flow,
    refresh_credentials,
)
from src.google.service.crud import (
    create_oauth_credential,
    create_state,
    get_credential,
    sync_gmail_profile,
    update_oauth_credential,
    upsert_credential,
)


# =============== OAUTH FLOW ===============
async def initiate_oauth2(
    db: AsyncSession,
    valid_user: User,
) -> GoogleOAuth2RedirectResponse:
    auth_url, state, code_verifier = init_flow()

    await create_state(
        db=db,
        valid_user=valid_user,
        state=state,
        code_verifier=code_verifier,
    )
    return GoogleOAuth2RedirectResponse(
        auth_url=auth_url,
        message="You are being redirected to Google for authorization.",
    )


async def exchange_code_for_credentials(
    db: AsyncSession,
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuth2CredentialResponse:
    credentials = await pkce_flow(exchange_code, oauth_state)
    new_record = build_app_oauth_credential(
        credentials,
        oauth_state.app_user_id,
    )
    existing_record = await get_credential(db, oauth_state.app_user_id)
    if existing_record is None:
        await create_oauth_credential(db, new_record, oauth_state)
    else:
        await update_oauth_credential(db, existing_record, new_record, oauth_state)

    return GoogleOAuth2CredentialResponse(
        app_user_id=new_record.app_user_id,
        scopes=new_record.scopes,
        expiry=new_record.expiry,
    )


async def connect_gmail_service(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuth2CredentialResponse:
    record = await refresh_credential_if_needed(db, record)
    credentials = build_google_credentials(record)
    credentials.expiry = record.expiry

    email_address = await get_authorized_email(credentials)
    record = await sync_gmail_profile(db, record, email_address)

    return GoogleOAuth2CredentialResponse(
        app_user_id=record.app_user_id,
        scopes=record.scopes,
        expiry=record.expiry,
    )


# =============== REFRESH FLOW ===============
async def refresh_credential_if_needed(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    creds = build_google_credentials(record)
    creds.expiry = record.expiry

    if creds.expired and creds.refresh_token:
        await refresh_credentials(creds)
        await upsert_credential(
            db=db,
            record=record,
            credentials=creds,
            email_address=record.email_address,
        )
        refreshed = await get_credential(db, record.app_user_id)
        if refreshed is not None:
            return refreshed

    return record
