from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.auth.schemas import AuthCreate
from src.auth.service import create_access_token, create_user


async def test_dashboard_update_orders_redirects_with_success_message(client, session):
    merchant = await create_user(
        AuthCreate(
            username="merchant_dashboard",
            email="merchant_dashboard@example.com",
            password="password123",
        ),
        session,
    )
    merchant.role = "merchant"
    await session.commit()

    token = create_access_token({"sub": str(merchant.id), "role": merchant.role})
    client.cookies.set("access_token", token.access_token)

    credential = SimpleNamespace(user_id=merchant.id, email_address="merchant@example.com")
    gmail_service = SimpleNamespace()

    with (
        patch("src.ssr.users.get_oauth_credential", new=AsyncMock(return_value=credential)),
        patch("src.ssr.users.sync_access_token", new=AsyncMock(return_value=credential)),
        patch("src.ssr.users.get_gmail_service", return_value=gmail_service),
        patch(
            "src.ssr.users.fetch_and_persist_benify_orders",
            new=AsyncMock(return_value={"persisted_count": 3}),
        ) as fetch_mock,
    ):
        response = await client.post(f"/users/{merchant.id}/dashboard/orders/update")

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == f"/users/{merchant.id}/dashboard?orders_status=success&orders_message=Updated+orders.+Persisted+3+orders."
    )
    fetch_mock.assert_awaited_once_with(
        db=session,
        gmail_service=gmail_service,
        merchant_id=merchant.id,
        max_results=100,
    )


async def test_dashboard_update_orders_redirects_with_error_when_google_not_connected(client, session):
    merchant = await create_user(
        AuthCreate(
            username="merchant_no_google",
            email="merchant_no_google@example.com",
            password="password123",
        ),
        session,
    )
    merchant.role = "merchant"
    await session.commit()

    token = create_access_token({"sub": str(merchant.id), "role": merchant.role})
    client.cookies.set("access_token", token.access_token)

    with (
        patch("src.ssr.users.get_oauth_credential", new=AsyncMock(return_value=None)),
        patch("src.ssr.users.fetch_and_persist_benify_orders", new=AsyncMock()) as fetch_mock,
    ):
        response = await client.post(f"/users/{merchant.id}/dashboard/orders/update")

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == f"/users/{merchant.id}/dashboard?orders_status=error&orders_message=Connect+Google+before+updating+orders."
    )
    fetch_mock.assert_not_awaited()
