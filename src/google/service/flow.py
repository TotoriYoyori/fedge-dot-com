from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState


from src.google.service.client import (
    fetch_google_oauth_state,
    fetch_google_oauth_credential,
    get_gmail_service,
    refresh_google_oauth_credential,
)
from src.google.service.crud import (
    create_or_replace_state,
    create_oauth_credential,
    get_oauth_credential,
    sync_gmail_profile,
    update_oauth_credential,
    upsert_credential,
)
from src.google.service.gmail import get_authorized_email


# =============== OAUTH2 INITIATE AND EXCHANGE FLOW ===============
async def initiate_oauth2(
    db: AsyncSession,
    valid_user: User,
) -> GoogleOAuthState:
    """Replace any lingering OAuth state and persist a fresh one for the user.

    Args:
        db: Active async database session used to clear prior state rows and store
            the newly generated OAuth state.
        valid_user: Authenticated app user starting the Google OAuth flow.

    Returns:
        GoogleOAuthState: Newly created OAuth state user_google_credential containing the
        authorization URL and persisted app-side state after any previous
        unconsumed state for the same user has been removed.

    Example:
        >>> async def run_example() -> str:
        ...     state = await initiate_oauth2(db, valid_user)
        ...     return state.auth_url
    """
    new_state = fetch_google_oauth_state(valid_user)

    return await create_or_replace_state(db, new_state)


async def exchange_code_for_credentials(
    db: AsyncSession,
    exchange_code: str,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    """Exchange a callback code and persist the resulting Google OAuth user_google_credential.

    Args:
        db: Active async database session used for user_google_credential lookup and writes.
        exchange_code: Authorization code returned by Google in the callback.
        oauth_state: Persisted OAuth state user_google_credential that scopes the exchange. The
            state user_google_credential is consumed by the downstream create or update operation
            once user_google_credential persistence succeeds.

    Returns:
        GoogleOAuthCredential: Persisted Google OAuth user_google_credential user_google_credential created
        or updated for the user.

    Example:
        >>> async def run_example() -> int:
        ...     user_google_credential = await exchange_code_for_credentials(
        ...         db, exchange_code, current_oauth_state
        ...     )
        ...     return user_google_credential.user_id
    """
    current_credential = await get_oauth_credential(db, oauth_state.user_id)

    new_credential = await fetch_google_oauth_credential(exchange_code, oauth_state)
    if current_credential is None:
        return await create_oauth_credential(db, new_credential, oauth_state)

    return await update_oauth_credential(db, current_credential, new_credential, oauth_state)


# =============== FLOW TO SYNC WITH GOOGLE'S SERVICES ===============
async def connect_gmail_service(
    db: AsyncSession,
    user_google_credential: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    service = get_gmail_service(user_google_credential)
    email_address = await get_authorized_email(service)

    return await sync_gmail_profile(db, user_google_credential, email_address)


# =============== REFRESH FLOW ===============
async def refresh_credential_if_needed(
    db: AsyncSession,
    user_google_credential: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    refreshed_credential = await refresh_google_oauth_credential(
        user_google_credential
    )
    if refreshed_credential is None:
        return user_google_credential

    await upsert_credential(
        db=db,
        record=user_google_credential,
        credentials=refreshed_credential,
        email_address=user_google_credential.email_address,
    )
    refreshed = await get_oauth_credential(db, user_google_credential.user_id)
    if refreshed is not None:
        return refreshed

    return user_google_credential
