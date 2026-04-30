from typing import Annotated, Callable

from fastapi import Cookie, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    AlreadyAuthenticated,
    InsufficientPermission,
    MalformedToken,
    UnauthenticatedUser,
    UsernameAlreadyExists,
    UserNotFound,
)
from src.auth.models import User
from src.auth.schemas import AuthCreate
from src.auth.security import AuthSecurity, oauth2_scheme
from src.auth.service import AuthService
from src.database import get_db


# --------------- TOKEN VERIFICATION INTERNALS
async def _verify_token(access_token: str, db: AsyncSession) -> User:
    """
    Private token verifier. For both API and SSR flow.

    Raises:
        UnauthenticatedUser: If the token is missing.
        MalformedToken: If the token is invalid or malformed.
        UserNotFound: If no user matches the token existing_record.
    """
    if not access_token:
        raise UnauthenticatedUser

    payload = AuthSecurity.verify_access_token(access_token)
    if not payload:
        raise MalformedToken

    user_id = payload.get("sub")
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise MalformedToken

    user = await AuthService.get_one_by("id", user_id_int, db)
    if not user:
        raise UserNotFound

    return user


# --------------- USER AUTHENTICATION DEPENDENCIES
async def valid_login_credentials(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Validate username and password from an urlencoded form. Use as dependency injection only.

    Raises:
        UnauthenticatedUser: If the username does not exist or the password is invalid.

    Example:
        >>> async def login(valid_user: Annotated[User, Depends(valid_login_credentials)]):
        >>>    if not valid_user:
        >>>        return None
        >>>    return valid_user
    """
    user = await AuthService.get_one_by("username", login_form.username, db)
    if not user or not AuthSecurity.verify_password(
        login_form.password, user.password_hash
    ):
        raise UnauthenticatedUser

    return user


async def valid_access_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Validate a JWT access token embedded in Headers from request. Use as dependency injection only.

    Raises:
        UnauthenticatedUser: If the token is missing.
        MalformedToken: If the token is invalid or malformed.
        UserNotFound: If no user matches the token existing_record.

    Example:
        >>> async def me(authorized_user: Annotated[User, Depends(valid_access_token)]):
        >>>     return authorized_user
    """
    return await _verify_token(token, db)


async def valid_cookie_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User | None:
    """
    Validate a JWT access token sent from browser cookies. Use as dependency injection only.

    Note:
        This function never raises authentication-related exceptions. Invalid,
        missing, or malformed tokens will result in None.

    Example:
        >>> async def register_page(request: Request, current_user: Annotated[User | None, Depends(valid_cookie_token)]):
        >>>     if current_user:
        >>>         return AuthRedirect.to_home()
        >>>     return templates.TemplateResponse()
    """
    try:
        return await _verify_token(access_token, db)
    except (UnauthenticatedUser, MalformedToken, UserNotFound):
        return None


def require_role(*roles: str, use_cookie: bool = False) -> Callable:
    """
    Enforce role-based access control. Orchestrate either valid_access_token or valid_cookie_token.
    Use as dependency injection only.

    Args:
        *roles (str): One or more role names permitted to access the resource.
        use_cookie (bool): If True, use cookie-based authentication (SSR).
            Otherwise, use Bearer token authentication (API).

    Returns:
        Callable: A dependency function checker() that validates the user's role and
        returns the authenticated user or raises.

    Raises:
        InsufficientPermission: If the authenticated user does not have one of the required roles.

    Example:
        >>> async def send_notify_email(
        >>>     valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
        >>>     send_context: SendContext
        >>> ) -> None:
    """
    check_cookie_or_token = valid_cookie_token if use_cookie else valid_access_token

    async def checker(user: Annotated[User, Depends(check_cookie_or_token)]) -> User:
        if user.role not in roles:
            raise InsufficientPermission
        return user

    return checker


# --------------- AUTHENTICATION STATUS CHECKS
async def not_currently_logged_in(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> bool | None:
    """
    Prevent authenticated users from accessing public auth routes (e.g., login, register) by checking JWT token
    embedded in Headers. Use as dependency injection only.

    Raises:
        AlreadyAuthenticated: If a valid token is present, indicating the user is already logged in.

    Example:
        >>> @router.post("/", dependencies=[Depends(not_currently_logged_in)])
        >>> async def register():
    """
    if token and AuthSecurity.verify_access_token(token):
        raise AlreadyAuthenticated

    return True


async def username_already_exists(
    auth_create: AuthCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> bool:
    """
    Check if a username already exists during registration by checking JSON existing_record's username entry.
    Use as dependency injection only.

    Raises:
        UsernameAlreadyExists: If the username is already taken.

    Example:
        >>> async def register(
        >>>     username_taken: Annotated[bool, Depends(username_already_exists)],
        >>> ) -> User | None:
    """
    user = await AuthService.get_one_by("username", auth_create.username, db)
    if user:
        raise UsernameAlreadyExists

    return False
