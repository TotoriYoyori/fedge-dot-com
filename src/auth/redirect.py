from fastapi import status
from fastapi.responses import RedirectResponse

from src.auth.schemas import Token
from src.auth.settings import auth_settings


# --------------- SSR REDIRECT HELPERS
class AuthRedirect:
    """
    Handling authentication redirects for SSR (server-side rendered) flows.

    Available methods:
        - to_home() -> RedirectResponse
        - store_cookie(token: Token) -> RedirectResponse
        - logout() -> RedirectResponse

    Example:
        >>> response = AuthRedirect.to_home()
        >>> response.status_code
        303
        >>> response.headers["location"]
        '/'
    """

    LOGIN_PAGE = "login.html"
    REGISTER_PAGE = "register.html"
    DASHBOARD_PAGE = "dashboard.html"

    @staticmethod
    def to_home() -> RedirectResponse:
        """
        Redirect the user to the home page.

        Returns:
            RedirectResponse: A 303 redirect response pointing to "/".
        """
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        return response

    @staticmethod
    def store_cookie(token: Token) -> RedirectResponse:
        """
        Store a JWT access token in an HTTP-only cookie AND redirect the user to home.

        Args:
            token (Token): The JWT token object containing the access token string.

        Returns:
            RedirectResponse: A redirect response to "/" with an authentication cookie set.

        Example:
            >>> token = Token(access_token="random.jwt.token", token_type="bearer")
            >>> response = AuthRedirect.store_cookie(token)
            >>> response.status_code
            303
            >>> "access_token" in response.headers.get("set-cookie", "")
            True
        """
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
        """
        Log out the user by removing the authentication cookie and redirecting to home.

        Returns:
            RedirectResponse: A 303 redirect response to "/" with the access token cookie removed.

        Example:
            >>> response = AuthRedirect.logout()
            >>> response.status_code
            303
            >>> "access_token" in response.headers.get("set-cookie", "")
            False
        """
        response = AuthRedirect.to_home()
        response.delete_cookie("access_token")
        return response
