from fastapi import status
from fastapi.responses import RedirectResponse


class UserRedirect:
    """Handling user-related redirects for SSR (server-side rendered) flows."""

    DASHBOARD_PAGE = "dashboard.html"

    @staticmethod
    def to_dashboard(user_id: int) -> RedirectResponse:
        """
        Redirect the user to their unique dashboard page.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            RedirectResponse: A 303 redirect response pointing to "/users/{user_id}/dashboard".
        """
        return RedirectResponse(
            url=f"/users/{user_id}/dashboard", status_code=status.HTTP_303_SEE_OTHER
        )
