from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.orders.service import fetch_and_persist_benify_orders, list_persisted_orders


async def test_fetch_and_persist_benify_orders_skips_malformed_messages(session):
    gmail_service = SimpleNamespace()
    messages = [
        {
            "body": (
                "Your order number:\tORDER-1001\n"
                "First name\tJane\n"
                "Surname\tDoe\n"
                "Office email\tjane@example.com\n"
                "Select treatment:\tMassage\n"
                "Choose location\tBerlin\n"
                "for delivery on 2026-05-01\n"
            )
        },
        {
            "body": "This is from Benify but does not contain a parseable order number.\n"
        },
    ]

    with patch(
        "src.orders.service.get_gmail_messages",
        new=AsyncMock(return_value={"messages": messages, "result_size_estimate": 2}),
    ):
        response = await fetch_and_persist_benify_orders(
            db=session,
            gmail_service=gmail_service,
            merchant_id=42,
            max_results=100,
        )

    persisted_orders = await list_persisted_orders(db=session, merchant_id=42)

    assert response["persisted_count"] == 1
    assert persisted_orders["result_size_estimate"] == 1
    assert persisted_orders["orders"][0].order_number == "ORDER-1001"
