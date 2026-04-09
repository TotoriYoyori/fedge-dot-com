from fastapi import HTTPException, status


DummyNameAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Another dummy with specified name already exists. Please try a different name.",
)

UnauthenticatedDummy = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Unauthenticated. Incorrect name or password.",
    headers={"WWW-Authenticate": "Bearer"},
)
