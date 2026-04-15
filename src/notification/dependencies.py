def craft_template_format(
    name: str = "",
    treatment: str = "treatments",
    order_number: str = "",
    location: str = "one of our clinics",
) -> dict:
    # FIXME: This dependencies is not to be kept long, and must be reformatted into cleaner
    # FIXME: architecture as soon as possible!
    """
    A simple query interface to input user information through REST API.
    """
    return {
        "name": name.strip().split()[0] if name.strip() else "",
        "treatment": treatment,
        "order_number": order_number,
        "location": location,
    }
