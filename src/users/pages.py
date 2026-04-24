from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request

from src.auth.dependencies import valid_cookie_token
from src.auth.models import User
from src.auth.redirect import AuthRedirect
from src.schemas import RouteDecoratorPreset
from src.templates import templates
from src.users.redirect import UserRedirect

# --------------- SSR PAGE ROUTER
page = APIRouter(prefix="/users", tags=["ssr"])


@page.get(
    "/{user_id}/dashboard",
    name="dashboard_page",
    summary="Renders the dashboard page for the authenticated user",
    **RouteDecoratorPreset.html_get(),
)
async def dashboard(
    request: Request,
    user_id: int,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
):
    if not current_user:
        return AuthRedirect.to_home()

    if current_user.id != user_id or current_user.role not in ['merchant', 'admin']:
        return UserRedirect.to_dashboard(current_user.id)

    return templates.TemplateResponse(
        request=request,
        name=UserRedirect.DASHBOARD_PAGE,
        context={"user": current_user},
    )
