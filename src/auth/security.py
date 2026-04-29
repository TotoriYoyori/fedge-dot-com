from datetime import UTC, datetime, timedelta
import json

from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash

from src.auth.schemas import Token
from src.auth.settings import auth_settings

# --------------- SECURITY PRIMITIVES
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# --------------- JWT AND CRYPTOGRAPHY SERVICES
class AuthSecurity:
    """
    Security utility class for authentication and JWT handling.

    Available static methods:
        - hash_password(password: str) -> str
        - verify_password(plain_password: str, hashed_password: str) -> bool
        - get_access_token_expires_at(expires_delta: timedelta | None = None) -> datetime
        - create_access_token(data: dict, expires_delta: timedelta | None = None) -> Token
        - assign_role(role_key: str | None) -> str
        - verify_access_token(token: str) -> dict | None
    """

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_token_expiry_timestamp(
        expires_delta: timedelta | None = None,
    ) -> datetime:
        """
        Calculate the datetime for when a JWT access token will expire.

        Args:
            expires_delta (timedelta | None): Optional custom duration for token validity.
                If not provided, the default value from settings is used.

        Returns:
            datetime: The computed expiration timestamp in UTC.

        Example:
            >>> AuthSecurity.get_token_expiry_timestamp()
            datetime.datetime(2026, 4, 23, 14, 30, 0) # This token will expire on 2026-04-23 at 14:30
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return datetime.now(UTC) + expires_delta

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: timedelta | None = None
    ) -> Token:
        """
        Create a JWT access token with an expiration timestamp of type bearer.

        Args:
            data (dict): Payload data. Can be customized to encode whatever server wants to know about user per token.
            (e.g. currently supports identifying user's id and role).
            expires_delta (timedelta | None): Optional custom expiration duration.
                If not provided, the default configured expiry is used.

        Returns:
            Token: A Token object containing the encoded JWT and token type.

        Example:
            >>> token = AuthSecurity.create_access_token({"sub": "user123"})
            >>> token.token_type
            'bearer'
            >>> isinstance(token.access_token, str)
            True
        """
        to_encode = data.copy()
        expire = AuthSecurity.get_token_expiry_timestamp(expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            auth_settings.SECRET_KEY.get_secret_value(),
            algorithm=auth_settings.ALGORITHM,
        )

        return Token(access_token=encoded_jwt, token_type="bearer")

    @staticmethod
    def assign_role(role_key: str | None) -> str:
        """
        Assign a user role based on an optional role key.

        Args:
            role_key (str | None): Optional key used to map a predefined role
                from environment variable DEV_ROLE_KEY (which is a dictionary).

        Returns:
            str: The resolved user role. Defaults to "user" if no valid key is provided.

        Example:
            >>> AuthSecurity.assign_role("thekey_to_give_admin_role")
            'admin'
            >>> AuthSecurity.assign_role(None)
            'user'
        """
        role = "user"
        if role_key:
            try:
                role_keys = json.loads(auth_settings.DEV_ROLE_KEYS)
                if role_key in role_keys:
                    role = role_keys[role_key]
            except (json.JSONDecodeError, TypeError):
                pass

        return role

    @staticmethod
    def verify_access_token(token: str) -> dict | None:
        """
        Verify a JWT access token and return its decoded payload if valid.

        Args:
            token (str): The JWT access token to validate.

        Returns:
            dict | None: The decoded token payload if valid, otherwise None.

        Example:
            >>> AuthSecurity.verify_access_token("valid.jwt.token")
            '{"sub": "user123", "role": "admin"}'
            >>> AuthSecurity.verify_access_token("invalid.token") is None
            True
        """
        try:
            payload = jwt.decode(
                token,
                auth_settings.SECRET_KEY.get_secret_value(),
                algorithms=[auth_settings.ALGORITHM],
                options={"require": ["exp", "sub", "role"]},
            )
        except jwt.InvalidTokenError:
            return None
        else:
            return payload
