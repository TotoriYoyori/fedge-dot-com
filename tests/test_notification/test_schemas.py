from pydantic import ValidationError
import pytest

from src.notification.schemas import SendContext, EmailSendResponse, TemplateFormat


def test_template_format_defaults():
    schema = TemplateFormat()

    assert schema.treatment == "en eller flera behandlingar"
    assert schema.location == "en av vara kliniker"
    assert schema.name is None
    assert schema.order_number is None


def test_template_format_validation():
    # treatment min_length=1
    with pytest.raises(ValidationError):
        TemplateFormat(treatment="")
    
    # treatment max_length=128
    with pytest.raises(ValidationError):
        TemplateFormat(treatment="a" * 129)


def test_send_context_validation():
    # Valid data
    valid_data = {
        "to_email": "test@example.com",
        "name": "John Doe",
        "subject_line": "Custom Subject"
    }
    schema = SendContext(**valid_data)
    assert schema.to_email == "test@example.com"
    assert schema.subject_line == "Custom Subject"

    # Invalid email
    with pytest.raises(ValidationError):
        SendContext(to_email="not-an-email")

    # subject_line max_length=64
    with pytest.raises(ValidationError):
        SendContext(to_email="test@example.com", subject_line="a" * 65)


def test_send_response_valid():
    # Only id
    schema = EmailSendResponse(id="re_123")
    assert schema.id == "re_123"
    assert schema.http_headers is None

    # Both id and headers
    headers = {"X-Custom": "Value"}
    schema = EmailSendResponse(id="re_456", http_headers=headers)
    assert schema.id == "re_456"
    assert schema.http_headers == headers


def test_send_response_missing_id():
    # Missing required 'id'
    with pytest.raises(ValidationError):
        EmailSendResponse()


def test_send_response_extra_fields():
    # Should ignore extra fields
    data = {"id": "re_789", "extra": "data"}
    schema = EmailSendResponse(**data)
    assert schema.id == "re_789"
    assert not hasattr(schema, "extra")


def test_schemas_extra_fields():
    data = {
        "to_email": "test@example.com",
        "extra_field": "some_value"
    }
    schema = SendContext(**data)

    assert not hasattr(schema, "extra_field")
