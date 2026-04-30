from anyio import to_thread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.google.exceptions import ClientSecretNotFound, FaultyFlow, InvalidPKCE
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.google.settings import google_settings


class GoogleOAuthSecurity:

    @staticmethod
    def _generate_base_flow(state: str | None = None) -> Flow:
        try:
            return Flow.from_client_secrets_file(
                google_settings.GOOGLE_CLIENT_SECRETS_FILE,
                scopes=google_settings.GOOGLE_SCOPES.split(","),
                redirect_uri=google_settings.GOOGLE_REDIRECT_URI,
                state=state,
            )
        except FileNotFoundError:
            raise ClientSecretNotFound

    @staticmethod
    def _verify_code_challege(flow: Flow, code_verifier: str) -> Flow:
        if code_verifier and flow.code_verifier == code_verifier:
            return flow

        raise InvalidPKCE


    @staticmethod
    def init_flow() -> tuple[str, str, str]:
        """Build the initial Google OAuth2 authorization flow and return outputs for state creation.

        Returns:
            tuple[str, str, str | None]: A tuple containing in order: the authorization
            URL, generated OAuth state, and optional PKCE code verifier.

        Raises:
            ClientSecretNotFound: If the configured Google client secret file cannot be found.
            FaultyFlow: If the flow, authorization URL, or state cannot be created.

        Example:
            >>> auth_url, state, code_verifier = GoogleOAuthSecurity.init_flow()
        """
        try:
            flow = GoogleOAuthSecurity._generate_base_flow()
            auth_url, state = flow.authorization_url(
                access_type=google_settings.FLOW_ACCESS_TYPE,
                include_granted_scopes=google_settings.FLOW_INCLUDE_GRANTED_SCOPES,
                prompt=google_settings.FLOW_PROMPT,
            )
        except Exception:
            raise FaultyFlow
        else:
            return auth_url, state, flow.code_verifier

    @staticmethod
    async def pkce_flow(exchange_code: str, oauth_state: GoogleOAuthState) -> Credentials:
        try:
            flow = GoogleOAuthSecurity._generate_base_flow(state=oauth_state.state)
        except Exception:
            raise FaultyFlow

        verified_flow = GoogleOAuthSecurity._verify_code_challege(flow, oauth_state.code_verifier)

        try:
            verified_flow.fetch_token(code=exchange_code)
        except Exception:
            raise FaultyFlow

        return verified_flow.credentials

    @staticmethod
    def build_credentials(record: GoogleOAuthCredential) -> Credentials:
        return Credentials(
            token=record.access_token,
            refresh_token=record.refresh_token,
            token_uri=record.token_uri,
            client_id=record.client_id,
            client_secret=record.client_secret,
            scopes=record.scopes.split(","),
        )

    @staticmethod
    async def refresh_credentials(credentials: Credentials) -> Credentials:
        await to_thread.run_sync(credentials.refresh, Request())
        return credentials

    @staticmethod
    def create_gmail_service(record: GoogleOAuthCredential):
        creds = GoogleOAuthSecurity.build_credentials(record)
        creds.expiry = record.expiry
        return GoogleOAuthSecurity.create_gmail_service_from_credentials(creds)

    @staticmethod
    def create_gmail_service_from_credentials(credentials: Credentials):
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)
