import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOOGLE_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/google/callback"
)
GOOGLE_SCOPES = [
    scope.strip()
    for scope in os.getenv(
        "GOOGLE_SCOPES",
        "openid,email,https://www.googleapis.com/auth/gmail.readonly",
    ).split(",")
    if scope.strip()
]
GOOGLE_CLIENT_SECRETS_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRETS_FILE",
    str((GOOGLE_DIR / "credentials.json").resolve()),
)
