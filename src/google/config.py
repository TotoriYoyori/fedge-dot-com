import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/google/callback")
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
    str(Path(__file__).with_name("credentials.json")),
)
