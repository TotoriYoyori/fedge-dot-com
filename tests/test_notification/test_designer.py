from src.notification.designer import EmailDesigner
from src.notification.schemas import SendContext


def test_write_email_plaintext_with_name():
    context = SendContext(
        to_email="test@example.com",
        name="John Doe",
        treatment="Massage",
        location="Malmo",
        order_number="12345"
    )
    text = EmailDesigner.write_email_plaintext(context)
    
    assert "Hej John Doe!" in text
    assert "Du har tidigare bestallt Massage" in text
    assert "Malmo" in text
    assert "Ordernummer: 12345" in text

def test_write_email_plaintext_no_name():
    context = SendContext(
        to_email="test@example.com",
        name=None,
        treatment="Massage",
        location="Malmo",
        order_number=None
    )
    text = EmailDesigner.write_email_plaintext(context)
    
    assert "Hej!" in text
    assert "Ordernummer" not in text

def test_write_email_html_rendering():
    # This tests that it calls jinja2 and renders something.
    # Note: it relies on the actual template file existing in TEMPLATES_DIR.
    context = SendContext(
        to_email="test@example.com",
        name="John Doe",
        treatment="Massage",
        location="Malmo",
        order_number="12345"
    )
    html = EmailDesigner.write_email_html(context)
    
    assert isinstance(html, str)
    assert len(html) > 0
    # Since we don't know the exact HTML structure without seeing the template,
    # we can at least check if the context variables are present if they are rendered.
    # But EmailDesigner.write_email_html uses .strip().split()[0] for name
    assert "John" in html
    assert "Massage" in html
    assert "12345" in html
