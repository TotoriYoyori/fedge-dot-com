from abc import ABC, abstractmethod

from fastapi import Request
from src.templates import templates


class BaseExceptionHandler(ABC):
    """Shard exception handler utilities. Domain handlers inherit and extend this."""

    def __init__(self, app):
        self.app = app
        self.register_exception_handlers()

    @staticmethod
    def _is_browser_request(request: Request) -> bool:
        return "text/html" in request.headers.get("accept", "")

    @staticmethod
    def _render_error(request: Request, page: str, error: str, status_code: int):
        return templates.TemplateResponse(
            request=request,
            name=page,
            context={"error": error},
            status_code=status_code,
        )

    @abstractmethod
    def register_exception_handlers(self) -> None:
        """Override in each domain to register domain-specific handlers."""
