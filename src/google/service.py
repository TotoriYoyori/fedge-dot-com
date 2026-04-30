from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.security import GoogleOAuthCredentialRecord, GoogleOAuthSecurity
from src.google.schemas import (
    GoogleOAuth2CredentialResponse,
    GoogleOAuth2RedirectResponse
)


# --------------- USE CASES (ORCHESTRATOR OF SERVICES AND SECURITY)
async def initiate_oauth2(db: AsyncSession, valid_user: User) -> GoogleOAuth2RedirectResponse:
    """Connect with Google, persist the connection state in DB, and return redirect payload.

    Args:
        db: Active async database session used to persist the OAuth state.
        valid_user: Authenticated application user starting the OAuth flow.

    Returns:
        GoogleOAuth2RedirectResponse: Redirect data containing the Google
        authorization URL and a user-facing message.

    Example:
        >>> async def run_example() -> str:
        ...     response = await initiate_oauth2(db, valid_user)
        ...     return response.auth_url
    """
    auth_url, state, code_verifier = GoogleOAuthSecurity.init_flow()

    await GoogleOAuthService.create_state(
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
    """Exchange callback code, persist base credentials, and consume the OAuth state.

    Args:
        db: Active async database session used for state consumption and credential persistence.
        exchange_code: Authorization code returned by Google's OAuth2 callback.
        oauth_state: Persisted OAuth state new_record containing the app user id and PKCE verifier.

    Returns:
        GoogleOAuth2CredentialResponse: Public callback response for the connected Google account.

    Example:
        >>> async def run_example() -> str:
        ...     response = await exchange_code_for_credentials(db, exchange_code, oauth_state)
        ...     return response.app_user_id
    """
    credentials = await GoogleOAuthSecurity.pkce_flow(exchange_code, oauth_state)
    new_record = GoogleOAuthSecurity.build_app_oauth_credential(
        credentials,
        oauth_state.app_user_id
    )
    existing_record = await GoogleOAuthService.get_credential(
        db,
        oauth_state.app_user_id,
    )
    if existing_record is None:
        await GoogleOAuthService.create_oauth_credential(db, new_record, oauth_state)
    else:
        await GoogleOAuthService.update_oauth_credential(db, existing_record, new_record, oauth_state)

    return GoogleOAuth2CredentialResponse(
        app_user_id=new_record.app_user_id,
        scopes=new_record.scopes,
        expiry=new_record.expiry,
    )


# --------------- CRUD SERVICES
class GoogleOAuthService:

    @staticmethod
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

    @staticmethod
    async def get_state(db: AsyncSession, state: str) -> GoogleOAuthState:
        result = await db.execute(
            select(GoogleOAuthState).where(GoogleOAuthState.state == state)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_state(db: AsyncSession, oauth_state: GoogleOAuthState) -> None:
        await db.delete(oauth_state)
        await db.commit()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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


async def refresh_credential_if_needed(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    creds = GoogleOAuthSecurity.build_google_credentials(record)
    creds.expiry = record.expiry
    if creds.expired and creds.refresh_token:
        await GoogleOAuthSecurity.refresh_credentials(creds)
        await GoogleOAuthService.upsert_credential(
            db=db,
            record=record,
            credentials=creds,
            email_address=record.email_address,
        )
        refreshed = await GoogleOAuthService.get_credential(db, record.app_user_id)
        if refreshed is not None:
            return refreshed

    return record


async def ensure_google_oauth_schema(db: AsyncSession) -> None:
    state_columns = await db.execute(text("PRAGMA table_info(google_oauth_states)"))
    state_column_names = {row[1] for row in state_columns.fetchall()}
    if "code_verifier" not in state_column_names:
        await db.execute(
            text("ALTER TABLE google_oauth_states ADD COLUMN code_verifier TEXT")
        )
        await db.commit()
