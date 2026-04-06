from fastapi import HTTPException, status


DummyNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="DUMMY not found.",
)

EmailAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="DUMMY email already exists.",
)
