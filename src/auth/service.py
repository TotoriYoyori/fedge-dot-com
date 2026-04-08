import jwt
from pwdlib import PasswordHash
from datetime import UTC, datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

from ..config import settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token") # match api for auth

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
