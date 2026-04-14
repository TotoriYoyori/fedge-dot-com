from fastapi import HTTPException, status

# --------------- CURRENT
UsernameAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username already exists. Please register with a different username.",
)

UnauthenticatedUser = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unauthenticated. Incorrect username or password.",
    headers={"WWW-Authenticate": "Bearer"},
)

MalformedToken = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Malformed token. Please log in and try again.",
    headers={"WWW-Authenticate": "Bearer"},
)

UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found.",
)
