class UsernameAlreadyExists(Exception):
    """Raised when a username is already taken during registration."""
    pass


class UnauthenticatedUser(Exception):
    """Raised when authentication fails (incorrect username or password)."""
    pass


class MalformedToken(Exception):
    """Raised when a JWT token is malformed or invalid."""
    pass


class UserNotFound(Exception):
    """Raised when a user is not found in the database."""
    pass


class AlreadyAuthenticated(Exception):
    """Raised when an authenticated user tries to access a guest-only resource."""
    pass
