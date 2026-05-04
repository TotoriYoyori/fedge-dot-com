from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.schemas import GoogleOAuth2CredentialCreate, GoogleOAuth2StateCreate


# =============== STATE CRUD ===============
async def create_state(
    db: AsyncSession,
    new_state: GoogleOAuth2StateCreate,
) -> GoogleOAuthState:
    new_oauth_state = GoogleOAuthState(**new_state.model_dump())
    db.add(new_oauth_state)

    await db.commit()
    await db.refresh(new_oauth_state)

    return new_oauth_state


async def get_state(db: AsyncSession, state: str) -> GoogleOAuthState:
    stmt = select(GoogleOAuthState).where(
        GoogleOAuthState.state == state
    )
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def delete_state(
    db: AsyncSession,
    oauth_state: GoogleOAuthState
) -> GoogleOAuthState:
    await db.delete(oauth_state)
    await db.commit()

    return oauth_state


# =============== CREDENTIAL CRUD ===============
async def create_oauth_credential(
    db: AsyncSession,
    new_credential: GoogleOAuth2CredentialCreate,
    current_oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    """Create and persist a Google OAuth credential, then consume the OAuth state.

    Args:
        db: Active async database session used for the credential insert.
        new_credential: Credential payload produced from the OAuth code exchange.
        current_oauth_state: Persisted OAuth state record that will be deleted as part of
            the same transaction after the credential is stored.

    Returns:
        GoogleOAuthCredential: Newly persisted Google OAuth credential record.

    Example:
        >>> async def run_example() -> int:
        ...     record = await create_oauth_credential(db, new_credential, current_oauth_state)
        ...     return record.user_id
    """
    new_credential = GoogleOAuthCredential(**new_credential.model_dump())

    db.add(new_credential)

    await db.delete(current_oauth_state)

    await db.commit()
    await db.refresh(new_credential)

    return new_credential


async def update_oauth_credential(
    db: AsyncSession,
    current_credential: GoogleOAuthCredential,
    new_credential: GoogleOAuth2CredentialCreate,
    current_oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    """Update a stored Google OAuth credential and consume the OAuth state.

    Args:
        db: Active async database session used for the credential update.
        current_credential: Existing persisted credential record to update in
            place.
        new_credential: Fresh credential payload produced from the latest OAuth
            code exchange.
        current_oauth_state: Persisted OAuth state record that will be deleted as part of
            the same transaction after the credential update is committed.

    Returns:
        GoogleOAuthCredential: Updated Google OAuth credential record.

    Example:
        >>> async def run_example() -> int:
        ...     record = await update_oauth_credential(
        ...         db, persisted_record, exchanged_record, current_oauth_state
        ...     )
        ...     return record.user_id
    """
    payload_data = new_credential.model_dump(
        exclude={"created_time", "updated_time"}
    )
    payload_data["refresh_token"] = (
        new_credential.refresh_token or current_credential.refresh_token
    )

    for field_name, field_value in payload_data.items():
        setattr(current_credential, field_name, field_value)

    current_credential.updated_time = new_credential.updated_time

    await db.delete(current_oauth_state)

    await db.commit()
    await db.refresh(current_credential)

    return current_credential


async def get_oauth_credential(
    db: AsyncSession,
    user_id: int,
) -> GoogleOAuthCredential | None:
    """Get the stored Google OAuth credential for a user from the app db.

    Args:
        db: Active async database session used to query the credential table.
        user_id: Application user identifier associated with the credential.

    Returns:
        GoogleOAuthCredential | None: Persisted credential record for the user, or
        ``None`` when no record exists.

    Example:
        >>> async def run_example() -> bool:
        ...     record = await get_oauth_credential(db, 42)
        ...     return record is not None
    """
    stmt = select(GoogleOAuthCredential).where(
        GoogleOAuthCredential.user_id == user_id
    )
    result = await db.execute(stmt)

    return result.scalar_one_or_none()


async def upsert_credential(
    db: AsyncSession,
    record: GoogleOAuthCredential,
    credentials: Credentials,
    email_address: str | None = None,
) -> GoogleOAuthCredential:
    record.access_token = credentials.token
    record.refresh_token = credentials.refresh_token or record.refresh_token
    record.token_uri = credentials.token_uri or record.token_uri
    record.client_id = credentials.client_id or record.client_id
    record.client_secret = credentials.client_secret or record.client_secret
    record.scopes = ",".join(credentials.scopes or []) or record.scopes
    record.expiry = credentials.expiry
    record.email_address = email_address or record.email_address
    record.updated_time = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)

    return record

# =============== EMAIL SERVICE CRUD ===============
async def sync_gmail_profile(
    db: AsyncSession,
    record: GoogleOAuthCredential,
    email_address: str | None,
) -> GoogleOAuthCredential:
    record.email_address = email_address or record.email_address
    record.updated_time = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)

    return record
