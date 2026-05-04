from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.schemas import (
    GoogleOAuth2CredentialResponse,
)

from src.google.service.client import (
    build_google_credentials,
    get_authorized_email,
    fetch_google_oauth_state,
    fetch_google_oauth_credential,
    refresh_credentials,
)
from src.google.service.crud import (
    create_state,
    create_oauth_credential,
    get_oauth_credential,
    sync_gmail_profile,
    update_oauth_credential,
    upsert_credential,
)


# =============== OAUTH2 INITIATE AND EXCHANGE FLOW ===============
async def initiate_oauth2(
    db: AsyncSession,
    valid_user: User,
) -> GoogleOAuthState:
    """Build and persist a Google OAuth state record for the user.

    Args:
        db: Active async database session used to store the generated OAuth state.
        valid_user: Authenticated app user starting the Google OAuth flow.

    Returns:
        GoogleOAuthState: Newly created OAuth state record containing the
        authorization URL and persisted app-side state.

    Example:
        >>> async def run_example() -> str:
        ...     state = await initiate_oauth2(db, valid_user)
        ...     return state.auth_url
    """
    new_state = fetch_google_oauth_state(valid_user)

    return await create_state(db, new_state)


async def exchange_code_for_credentials(
    db: AsyncSession,
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    """Exchange a callback code and persist the resulting Google OAuth credential.

    Args:
        db: Active async database session used for credential lookup and writes.
        exchange_code: Authorization code returned by Google in the callback.
        oauth_state: Persisted OAuth state record that scopes the exchange. The
            state record is consumed by the downstream create or update operation
            once credential persistence succeeds.

    Returns:
        GoogleOAuthCredential: Persisted Google OAuth credential record created
        or updated for the user.

    Example:
        >>> async def run_example() -> int:
        ...     record = await exchange_code_for_credentials(
        ...         db, exchange_code, current_oauth_state
        ...     )
        ...     return record.user_id
    """
    current_credential = await get_oauth_credential(db, oauth_state.user_id)

    new_credential = await fetch_google_oauth_credential(exchange_code, oauth_state)
    if current_credential is None:
        return await create_oauth_credential(db, new_credential, oauth_state)

    return await update_oauth_credential(db, current_credential, new_credential, oauth_state)


# =============== FLOW TO SYNC WITH GOOGLE'S SERVICES ===============
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
        user_id=record.user_id,
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
        refreshed = await get_oauth_credential(db, record.user_id)
        if refreshed is not None:
            return refreshed

    return record
