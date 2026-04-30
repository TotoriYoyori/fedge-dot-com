from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import BaseExceptionHandler


class FaultyFlow(Exception):
    pass


class ClientSecretNotFound(Exception):
    pass


class MalformedState(Exception):
    pass


class ExchangeCodeNotFound(Exception):
    pass


class StateNotFound(Exception):
    pass


class InvalidPKCE(Exception):
    pass


class CredentialNotFound(Exception):
    pass


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

        @self.app.exception_handler(MalformedState)
        async def malformed_state_handler(request: Request, _exc: MalformedState):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Malformed Google OAuth callback state."},
            )

        @self.app.exception_handler(ExchangeCodeNotFound)
        async def exchange_code_not_found_handler(
            request: Request, _exc: ExchangeCodeNotFound
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Google OAuth exchange code not found."},
            )

        @self.app.exception_handler(StateNotFound)
        async def state_not_found_handler(request: Request, _exc: StateNotFound):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Google OAuth state not found."},
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
