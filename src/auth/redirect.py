from fastapi import status
from fastapi.responses import RedirectResponse

from src.auth.schemas import Token
from src.auth.settings import auth_settings


class AuthRedirect:
    LOGIN_PAGE = "login.html"
    REGISTER_PAGE = "register.html"
    DASHBOARD_PAGE = "dashboard.html"

    @staticmethod
    def to_home() -> RedirectResponse:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response

    @staticmethod
    def store_cookie(token: Token) -> RedirectResponse:
        response = AuthRedirect.to_home()
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,  # JS cannot access this
            secure=True,  # HTTPS only in production
            samesite="lax",  # CSRF protection
            max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response

    @staticmethod
    def logout() -> RedirectResponse:
        response = AuthRedirect.to_home()
        response.delete_cookie("access_token")
        return response
