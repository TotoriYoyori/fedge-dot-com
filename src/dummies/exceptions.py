from fastapi import HTTPException, status


DummyWithNameExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="A dummy with this name already exists. Please try a different one.",
)

DummyNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="DUMMY not found.",
)

EmailAlreadyExists = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="DUMMY email already exists.",
)
