import datetime as dt
from unittest.mock import patch

import asyncer
import pytest

from src.notification.schemas import SendContext, EmailSendResponse
from src.notification.service import send_email


@pytest.fixture
def fake_context():
    def _create(to_email: str) -> SendContext:
        payload = {
            "name": "Harry Testing",
            "location": "Hogwarts School of Witchcraft and Wizardry",
            "order_number": "xXHeadshot360Xx",
            "subject_line": "You are a Wizard, Harry!",
            "to_email": to_email,
        }
        return SendContext(**payload)

    return _create


async def test_send_email_mocked(fake_context) -> None:
    with patch("resend.Emails.send") as mock_resend:
        mock_resend.return_value = {"id": "test_id", "http_headers": {"X-Test": "test"}}
        context = fake_context(to_email="test@example.com")
        response = await send_email(context)

        assert isinstance(response, EmailSendResponse)
        assert response.id == "test_id"

        # Verify Resend calls
        mock_resend.assert_called_once()


async def test_send_email_concurrent(fake_context) -> None:
    # Using the original task group test but with mocking
    with patch("resend.Emails.send") as mock_resend:
        mock_resend.return_value = {"id": "test_id", "http_headers": {"X-Test": "test"}}
        async with asyncer.create_task_group() as tg:
            a_send = tg.soonify(send_email)(
                fake_context(to_email="stan.mng@gmail.com"),
            )
            b_send = tg.soonify(send_email)(
                fake_context(to_email="lilmissmj.0606@gmail.com"),
            )
            c_send = tg.soonify(send_email)(
                fake_context(to_email="teainbasement@gmail.com"),
            )

        all_response = [a_send.value, b_send.value, c_send.value]

        assert all(isinstance(response, EmailSendResponse) for response in all_response)

        assert mock_resend.call_count == 3
