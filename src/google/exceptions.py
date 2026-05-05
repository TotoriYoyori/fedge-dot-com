from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import BaseExceptionHandler


# =============== DOMAIN EXCEPTIONS ===============
class FaultyFlow(Exception):
    pass


class ClientSecretNotFound(Exception):
    pass


class InvalidGoogleOAuthCallback(Exception):
    pass


class InvalidPKCE(Exception):
    pass


class CredentialNotFound(Exception):
    pass


class NotRefreshableCredential(Exception):
    pass


# =============== EXCEPTION HANDLERS ===============
class GoogleExceptionHandler(BaseExceptionHandler):
    def register_exception_handlers(self) -> None:
        @self.app.exception_handler(ClientSecretNotFound)
        async def client_secret_not_found_handler(
            request: Request, _exc: ClientSecretNotFound
        ):
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Google OAuth client secret file was not found."},
            )

        @self.app.exception_handler(FaultyFlow)
        async def faulty_flow_handler(request: Request, _exc: FaultyFlow):
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": (
                        "Google OAuth flow, authorization URL, or state could not "
                        "be created."
                    )
                },
            )

        @self.app.exception_handler(InvalidGoogleOAuthCallback)
        async def invalid_google_oauth_callback_handler(
            request: Request, _exc: InvalidGoogleOAuthCallback
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": (
                        "Invalid Google OAuth callback. Please restart the Google "
                        "OAuth flow."
                    )
                },
            )

        @self.app.exception_handler(InvalidPKCE)
        async def invalid_pkce_handler(request: Request, _exc: InvalidPKCE):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Google OAuth PKCE verifier is invalid."},
            )

        @self.app.exception_handler(CredentialNotFound)
        async def credential_not_found_handler(
            request: Request, _exc: CredentialNotFound
        ):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Google OAuth credential not found for app user."},
            )

        @self.app.exception_handler(NotRefreshableCredential)
        async def not_refreshable_credential_handler(
            request: Request, _exc: NotRefreshableCredential
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": (
                        "Google OAuth credential is expired and cannot be refreshed. "
                        "Please redo the Google OAuth flow to obtain a new credential."
                    )
                },
            )
