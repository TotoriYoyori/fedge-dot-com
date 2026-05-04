from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState

from src.google.service.client import GoogleOAuthCredentialRecord


# =============== STATE CRUD ===============
async def create_state(
    db: AsyncSession,
    valid_user: User,
    state: str,
    code_verifier: str | None,
) -> GoogleOAuthState:
    new_oauth_state = GoogleOAuthState(
        state=state,
        app_user_id=str(valid_user.id),
        code_verifier=code_verifier,
        created_time=datetime.now(timezone.utc),
    )
    db.add(new_oauth_state)

    await db.commit()
    await db.refresh(new_oauth_state)

    return new_oauth_state


async def get_state(db: AsyncSession, state: str) -> GoogleOAuthState:
    result = await db.execute(
        select(GoogleOAuthState).where(GoogleOAuthState.state == state)
    )
    return result.scalar_one_or_none()


async def delete_state(db: AsyncSession, oauth_state: GoogleOAuthState) -> None:
    await db.delete(oauth_state)
    await db.commit()


# =============== CREDENTIAL CRUD ===============
async def create_oauth_credential(
    db: AsyncSession,
    new_record: GoogleOAuthCredentialRecord,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    payload_data = new_record.model_dump()
    now = datetime.now(timezone.utc)
    new_record = GoogleOAuthCredential(
        **payload_data,
        created_time=now,
        updated_time=now,
    )
    db.add(new_record)
    await db.delete(oauth_state)

    await db.commit()
    await db.refresh(new_record)

    return new_record


async def update_oauth_credential(
    db: AsyncSession,
    new_record: GoogleOAuthCredential,
    existing_record: GoogleOAuthCredentialRecord,
    oauth_state: GoogleOAuthState,
) -> GoogleOAuthCredential:
    payload_data = existing_record.model_dump()
    payload_data["refresh_token"] = (
        existing_record.refresh_token or new_record.refresh_token
    )
    for field_name, field_value in payload_data.items():
        setattr(new_record, field_name, field_value)

    new_record.updated_time = datetime.now(timezone.utc)

    await db.delete(oauth_state)
    await db.commit()
    await db.refresh(new_record)

    return new_record


async def get_credential(
    db: AsyncSession,
    app_user_id: str,
) -> GoogleOAuthCredential | None:
    result = await db.execute(
        select(GoogleOAuthCredential).where(
            GoogleOAuthCredential.app_user_id == app_user_id
        )
    )
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
