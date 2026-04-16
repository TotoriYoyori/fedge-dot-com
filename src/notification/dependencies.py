from src.notification.schemas import TemplateFormat


def craft_template_format(
    name: str = "",
    treatment: str = "en av vara tjanster",
    order_number: str = "",
    location: str = "en av vara kliniker",
) -> TemplateFormat:
    # FIXME: This dependencies is not to be kept long, and must be reformatted into cleaner
    # FIXME: architecture as soon as possible!
    """
    A simple query interface to input user information through REST API.
    """
    return TemplateFormat(
        name=name.strip().split()[0] if name.strip() else "",
        treatment=treatment,
        order_number=order_number,
        location=location,
    )
