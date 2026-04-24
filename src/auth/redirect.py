from fastapi import status
from fastapi.responses import RedirectResponse

from src.auth.models import User
from src.auth.schemas import Token
from src.auth.security import AuthSecurity
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
    def create_cookie(user: User, redirect_url: str = "/") -> RedirectResponse:
        """
        Create and store a JWT access token in an HTTP-only cookie AND redirect the user.

        Args:
            user (User): A User object.
            redirect_url (str): The URL to redirect to after setting the cookie. Defaults to "/".

        Returns:
            RedirectResponse: A redirect response to the specified URL with an authentication cookie set.

        Example:
            >>> user = User(id=1, role="user")
            >>> response = AuthRedirect.create_cookie(user, "/dashboard")
            >>> response.status_code
            303
            >>> "access_token" in response.headers.get("set-cookie", "")
            True
        """
        token = AuthSecurity.create_access_token(
            data={"sub": str(user.id), "role": str(user.role)},
        )

        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
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
