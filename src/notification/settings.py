from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader


class NotificationSettings:
    TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
    DEFAULT_TEMPLATE_NAME = "ho_2.html"


template_env = Environment(
    loader=FileSystemLoader(str(NotificationSettings.TEMPLATES_DIR))
)
template_renderer = Jinja2Templates(directory=str(NotificationSettings.TEMPLATES_DIR))
