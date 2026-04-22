from fastapi import status
from fastapi.responses import RedirectResponse

from src.auth.settings import auth_settings
from src.auth.schemas import Token


class AuthResponse:

    @staticmethod
    def store_cookie_response(token: Token) -> RedirectResponse:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,  # JS cannot access this
            secure=True,  # HTTPS only in production
            samesite="lax",  # CSRF protection
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response
