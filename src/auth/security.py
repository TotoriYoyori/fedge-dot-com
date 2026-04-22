from datetime import UTC, datetime, timedelta
import json

from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash

from src.auth.schemas import Token
from src.auth.settings import auth_settings


# --------------- GLOBAL INSTANCE
password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# --------------- SECURITY LAYER
class AuthSecurity:
    """
    A wrapper class for security-related utilities.

    Provides functions for hashing passwords, verifying passwords,
    creating JWT access tokens, and verifying access tokens.

    Example usage:
        >>> from src.auth.security import AuthSecurity

        >>> hashed = AuthSecurity.hash_password("my_secret")
        >>> AuthSecurity.verify_password("my_secret", hashed)
        True
        >>> access_token = AuthSecurity.create_access_token({"sub": "user123"})
        >>> AuthSecurity.verify_access_token(access_token)
        'user123'
    """

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_access_token_expires_at(
        expires_delta: timedelta | None = None,
    ) -> datetime:
        if expires_delta is None:
            expires_delta = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return datetime.now(UTC) + expires_delta

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: timedelta | None = None
    ) -> Token:
        """Create a JWT access access_token."""
        to_encode = data.copy()
        expire = AuthSecurity.get_access_token_expires_at(expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            auth_settings.SECRET_KEY.get_secret_value(),
            algorithm=auth_settings.ALGORITHM,
        )

        return Token(access_token=encoded_jwt, token_type="bearer")

    @staticmethod
    def assign_role(role_key: str | None) -> str:
        """Determine user's role based on provided key and system configuration."""
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
        """Verify a JWT access access_token and return the payload if valid."""
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
