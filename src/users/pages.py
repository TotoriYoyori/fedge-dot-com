from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import valid_cookie_token
from src.auth.models import User
from src.database import get_db
from src.orders.service import list_persisted_orders
from src.schemas import RouteDecoratorPreset
from src.templates import Redirect, templates
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
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        return Redirect.to_home()

    if current_user.id != user_id and current_user.role != 'admin':
        return UserRedirect.to_dashboard(current_user.id)

    orders_response = await list_persisted_orders(db=db, merchant_id=user_id)

    return templates.TemplateResponse(
        request=request,
        name=UserRedirect.DASHBOARD_PAGE,
        context={
            "user": current_user,
            "orders": orders_response["orders"],
            "orders_count": orders_response["result_size_estimate"],
        },
    )
