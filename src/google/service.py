from datetime import datetime, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.google.models import GoogleOAuthCredential, GoogleOAuthState


class GoogleOAuthService:
    @staticmethod
    async def create_state(
        db: AsyncSession,
        state: str,
        app_user_id: str,
        code_verifier: str | None = None,
    ) -> GoogleOAuthState:
        oauth_state = GoogleOAuthState(
            state=state,
            app_user_id=app_user_id,
            code_verifier=code_verifier,
            created_at=datetime.now(timezone.utc),
        )
        db.add(oauth_state)
        await db.commit()
        await db.refresh(oauth_state)
        return oauth_state

    @staticmethod
    async def consume_state(db: AsyncSession, state: str) -> GoogleOAuthState | None:
        result = await db.execute(
            select(GoogleOAuthState).where(GoogleOAuthState.state == state)
        )
        oauth_state = result.scalar_one_or_none()
        if oauth_state is None:
            return None

        await db.delete(oauth_state)
        await db.commit()
        return oauth_state

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
        app_user_id: str,
        credentials: Credentials,
        email_address: str | None = None,
    ) -> GoogleOAuthCredential:
        record = await GoogleOAuthService.get_credential(db, app_user_id)
        now = datetime.now(timezone.utc)
        scopes = ",".join(credentials.scopes or [])

        if record is None:
            record = GoogleOAuthCredential(
                app_user_id=app_user_id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri or "https://oauth2.googleapis.com/token",
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                scopes=scopes,
                expiry=credentials.expiry,
                email_address=email_address,
                created_at=now,
                updated_at=now,
            )
            db.add(record)
        else:
            record.access_token = credentials.token
            record.refresh_token = credentials.refresh_token or record.refresh_token
            record.token_uri = credentials.token_uri or record.token_uri
            record.client_id = credentials.client_id or record.client_id
            record.client_secret = credentials.client_secret or record.client_secret
            record.scopes = scopes or record.scopes
            record.expiry = credentials.expiry
            record.email_address = email_address or record.email_address
            record.updated_at = now

        await db.commit()
        await db.refresh(record)
        return record


def build_credentials(record: GoogleOAuthCredential) -> Credentials:
    return Credentials(
        token=record.access_token,
        refresh_token=record.refresh_token,
        token_uri=record.token_uri,
        client_id=record.client_id,
        client_secret=record.client_secret,
        scopes=record.scopes.split(","),
    )


async def refresh_credential_if_needed(
    db: AsyncSession,
    record: GoogleOAuthCredential,
) -> GoogleOAuthCredential:
    creds = build_credentials(record)
    creds.expiry = record.expiry
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        await GoogleOAuthService.upsert_credential(
            db=db,
            app_user_id=record.app_user_id,
            credentials=creds,
            email_address=record.email_address,
        )
        refreshed = await GoogleOAuthService.get_credential(db, record.app_user_id)
        if refreshed is not None:
            return refreshed

    return record


def create_gmail_service(record: GoogleOAuthCredential):
    creds = build_credentials(record)
    creds.expiry = record.expiry
    return create_gmail_service_from_credentials(creds)


def create_gmail_service_from_credentials(credentials: Credentials):
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


async def ensure_google_oauth_schema(db: AsyncSession) -> None:
    state_columns = await db.execute(text("PRAGMA table_info(google_oauth_states)"))
    state_column_names = {row[1] for row in state_columns.fetchall()}
    if "code_verifier" not in state_column_names:
        await db.execute(text("ALTER TABLE google_oauth_states ADD COLUMN code_verifier TEXT"))
        await db.commit()
