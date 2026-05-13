from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import BaseExceptionHandler


class EmailDeliveryError(Exception):
    pass


class EmailResponseMismatch(Exception):
    pass


# --------------- FASTAPI EXCEPTION HANDLERS
class NotificationExceptionHandler(BaseExceptionHandler):
    def register_exception_handlers(self) -> None:
        @self.app.exception_handler(EmailDeliveryError)
        async def email_delivery_error_handler(
            request: Request, _exc: EmailDeliveryError
        ):
            if self._is_browser_request(request):
                return self._render_error(
                    request,
                    "error.html",  # or whatever your generic error page is
                    "We couldn't send the email. Please try again later.",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Failed to send email."},
            )

        @self.app.exception_handler(EmailResponseMismatch)
        async def email_response_mismatch_handler(
            request: Request, _exc: EmailResponseMismatch
        ):
            if self._is_browser_request(request):
                return self._render_error(
                    request,
                    "error.html",
                    "The email provider returned an unexpected response. Please try again later.",
                    status.HTTP_502_BAD_GATEWAY,
                )
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": "Email provider returned an unexpected response."},
            )
