
class DummyWithNameExists(Exception):
    """Raised when a dummy with the same name already exists."""
    pass


class DummyNotFound(Exception):
    """Raised when a dummy cannot be found in the database."""
    pass


class EmailAlreadyExists(Exception):
    """Raised when an email is already associated with another dummy."""
    pass
