from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import BaseExceptionHandler


class FlowNotFound(Exception):
    pass


class MalformedState(Exception):
    pass


class ExchangeCodeNotFound(Exception):
    pass


class StateNotFound(Exception):
    pass


class GoogleExceptionHandler(BaseExceptionHandler):
    def register_exception_handlers(self) -> None:
        @self.app.exception_handler(FlowNotFound)
        async def flow_not_found_handler(request: Request, _exc: FlowNotFound):
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Google OAuth flow could not be created."},
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
