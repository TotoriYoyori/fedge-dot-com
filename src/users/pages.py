from typing import Annotated, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.redirect import valid_cookie_token
from src.database import get_db
from src.google.service import get_gmail_service, sync_access_token
from src.google.service.crud import get_oauth_credential
from src.orders.service import fetch_and_persist_benify_orders, list_persisted_orders
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
    orders_status = request.query_params.get("orders_status")
    orders_message = request.query_params.get("orders_message")

    return templates.TemplateResponse(
        request=request,
        name=UserRedirect.DASHBOARD_PAGE,
        context={
            "user": current_user,
            "dashboard_user_id": user_id,
            "orders": orders_response["orders"],
            "orders_count": orders_response["result_size_estimate"],
            "orders_status": orders_status,
            "orders_message": orders_message,
        },
    )


@page.post(
    "/{user_id}/dashboard/orders/update",
    name="dashboard_update_orders",
    summary="Fetch Benify orders for the dashboard owner and reload the dashboard",
    **RouteDecoratorPreset.html_post(),
)
async def dashboard_update_orders(
    user_id: int,
    current_user: Annotated[Optional[User], Depends(valid_cookie_token)],
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        return Redirect.to_home()

    if current_user.id != user_id and current_user.role != "admin":
        return UserRedirect.to_dashboard(current_user.id)

    record = await get_oauth_credential(db, user_id)
    if record is None or record.email_address is None:
        return _dashboard_redirect(
            user_id=user_id,
            orders_status="error",
            orders_message="Connect Google before updating orders.",
        )

    record = await sync_access_token(db, record)
    gmail_service = get_gmail_service(record)
    fetch_response = await fetch_and_persist_benify_orders(
        db=db,
        gmail_service=gmail_service,
        merchant_id=record.user_id,
        max_results=100,
    )
    persisted_count = fetch_response["persisted_count"]
    order_label = "order" if persisted_count == 1 else "orders"

    return _dashboard_redirect(
        user_id=user_id,
        orders_status="success",
        orders_message=f"Updated orders. Persisted {persisted_count} {order_label}.",
    )


def _dashboard_redirect(
    user_id: int,
    orders_status: str,
    orders_message: str,
) -> RedirectResponse:
    query_string = urlencode(
        {
            "orders_status": orders_status,
            "orders_message": orders_message,
        }
    )
    return RedirectResponse(
        url=f"/users/{user_id}/dashboard?{query_string}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
