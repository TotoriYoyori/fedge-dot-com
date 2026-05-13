from src.notification.schemas import EmailSendPayload
from src.templates import notification_email_template

# =============== TEXT BODY TEMPLATE ===============
EMAIL_PLAINTEXT_TEMPLATE = (
    "Hej{greeting_name}!\n\n"
    "En liten paminnelse att boka din behandling.\n\n"
    "Du har tidigare bestallt {treatment} hos oss pa Hanna & Ong "
    "med ditt friskvardsbidrag, men har annu inte bokat din tid.\n\n"
    "Klicka och boka din tid via Bokadirekt pa {location}.\n\n"
    "Malmo: https://www.bokadirekt.se/places/"
    "hanna-ong-therapy-art-limhamn-malmo-55196\n"
    "Helsingborg: https://www.bokadirekt.se/places/"
    "hanna-ong-therapy-art-helsingborg-39960\n\n"
    "Med vanliga halsningar,\n\n"
    "Om du redan har bokat hos oss, ignorera garna detta meddelande."
    "{order_number_line}\n\n"
    "(c) 2026 Hanna & Ong"
)

# =============== DRAFTING MESSAGE FUNCTIONS ===============
def write_email_html(send_payload: EmailSendPayload) -> str:
    return notification_email_template.render(
        name=send_payload.name.strip().split()[0] if send_payload.name else "",
        treatment=send_payload.treatment,
        location=send_payload.location,
        order_number=send_payload.order_number,
    )


def write_email_plaintext(send_payload: EmailSendPayload) -> str:
    greeting_name = f" {send_payload.name}" if send_payload.name else ""
    order_number_line = (
        f"\nOrdernummer: {send_payload.order_number}"
        if send_payload.order_number
        else ""
    )

    return EMAIL_PLAINTEXT_TEMPLATE.format(
        greeting_name=greeting_name,
        treatment=send_payload.treatment,
        location=send_payload.location,
        order_number_line=order_number_line,
    )
