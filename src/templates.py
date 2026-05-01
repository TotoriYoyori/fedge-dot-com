from pathlib import Path

from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader


SRC_DIR = Path(__file__).resolve().parent


class Redirect:
    BASE = "base.html"
    SAMPLE = "sample.html"
    AUTH_BASE = "auth_base.html"
    AUTH_LOGIN = "login.html"
    AUTH_REGISTER = "register.html"
    LANDING_HOME = "home.html"
    NOTIFICATION_SEND = "send_notification.html"
    NOTIFICATION_HO_1 = "ho_1.html"
    NOTIFICATION_HO_2 = "ho_2.html"
    NOTIFICATION_HO_3 = "ho_3.html"
    USERS_DASHBOARD = "dashboard.html"

    @staticmethod
    def to_home() -> RedirectResponse:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# --------------- TEMPLATE DIRECTORY AUTO-DETECTION
def _discover_dirs(folder_name: str) -> list[str]:
    """
    Search the source directory and its immediate subdirectories for matching folder_name.

    Example:
        >>> _discover_dirs("templates")
        ['.../project/templates',
         '.../project/module_a/templates',
         '.../project/module_b/templates']
    """
    dirs: list[str] = []

    # ----- Search Base and Domains
    shared_dir = SRC_DIR / folder_name
    if shared_dir.exists():
        dirs.append(str(shared_dir))

    for path in sorted(SRC_DIR.iterdir()):
        candidate = path / folder_name
        if path.is_dir() and candidate.exists():
            dirs.append(str(candidate))

    return dirs


# --------------- JINJA2 TEMPLATE RENDERING ENGINE
page_loader = FileSystemLoader(_discover_dirs("templates"))
page_env = Environment(loader=page_loader)
templates = Jinja2Templates(env=page_env)
