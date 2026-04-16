from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationSettings(BaseSettings):
    TEMPLATES_DIR: str = str(Path(__file__).resolve().parent / "templates")
    DEFAULT_TEMPLATE_NAME: str = "ho_3.html"

    ENVIRONMENT: str

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str

    SANDBOX_SMTP_HOST: str | None = None
    SANDBOX_SMTP_PORT: int | None = None
    SANDBOX_SMTP_USERNAME: str | None = None
    SANDBOX_SMTP_PASSWORD: str | None = None
    SANDBOX_SMTP_FROM_NAME: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @property
    def smtp_host(self) -> str:
        if self.ENVIRONMENT.lower() == "local" and self.SANDBOX_SMTP_HOST:
            return self.SANDBOX_SMTP_HOST
        return self.SMTP_SERVER

    @property
    def smtp_port(self) -> int:
        if self.ENVIRONMENT.lower() == "local" and self.SANDBOX_SMTP_PORT:
            return self.SANDBOX_SMTP_PORT
        return self.SMTP_PORT

    @property
    def smtp_username(self) -> str:
        if self.ENVIRONMENT.lower() == "local" and self.SANDBOX_SMTP_USERNAME:
            return self.SANDBOX_SMTP_USERNAME
        return self.SMTP_USERNAME

    @property
    def smtp_password(self) -> str:
        if self.ENVIRONMENT.lower() == "local" and self.SANDBOX_SMTP_PASSWORD:
            return self.SANDBOX_SMTP_PASSWORD
        return self.SMTP_PASSWORD

    @property
    def smtp_from_name(self) -> str:
        if self.ENVIRONMENT.lower() == "local" and self.SANDBOX_SMTP_FROM_NAME:
            return self.SANDBOX_SMTP_FROM_NAME
        return self.SMTP_FROM_NAME


notification_settings = NotificationSettings()

template_env = Environment(
    loader=FileSystemLoader(notification_settings.TEMPLATES_DIR)
)
template_renderer = Jinja2Templates(directory=notification_settings.TEMPLATES_DIR)
