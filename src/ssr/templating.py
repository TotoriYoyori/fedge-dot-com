from pathlib import Path

from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

SSR_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SSR_DIR / "templates"


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


# --------------- JINJA2 TEMPLATE RENDERING ENGINE
page_loader = FileSystemLoader(str(TEMPLATES_DIR))
page_env = Environment(loader=page_loader)
templates = Jinja2Templates(env=page_env)
notification_email_template = page_env.get_template(Redirect.NOTIFICATION_HO_3)
