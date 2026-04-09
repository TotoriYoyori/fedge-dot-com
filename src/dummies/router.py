from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..authentication.dependencies import dummy_with_name_exists
from ..database import get_db
from .dependencies import valid_dummy_id
from .models import Dummy
from .service import DummyService
from .schemas import (
    DummyCreate,
    DummyUpdate,
    DummyPatch,
    DummyResponse,
    DummyDeleteResponse,
    DummyPrivate
)

# --------------- ROUTING TO http://mysite.com/dummies
router = APIRouter(prefix="/dummies", tags=["dummies"])


@router.post(
    "/",
    response_model=DummyResponse,
    status_code=status.HTTP_200_OK,
    summary="!ADMIN ONLY! Create New Dummy",
    description="God-mode endpoint for manually creating dummy users outside the normal registration flow.",
)
async def godspawn_dummy(
    authentication_create: DummyCreate,
    dummy_already_exists: bool = Depends(dummy_with_name_exists),
    db: AsyncSession = Depends(get_db)
):
    if dummy_already_exists:
        return None

    return await DummyService.create_dummy(authentication_create, db)


@router.get("/", response_model=list[DummyResponse], status_code=status.HTTP_200_OK)
async def get_all_dummies(
    db: AsyncSession = Depends(get_db)
):
    return await DummyService.get_all(db)

# FIXME: Bring me back to normal version when u r done testing >> response_model=DummyResponse
@router.get("/{dummy_id}", response_model=DummyResponse, status_code=status.HTTP_200_OK)
async def get_dummy(
    dummy: DummyResponse = Depends(valid_dummy_id),
    db: AsyncSession = Depends(get_db)
):
    return dummy


@router.put("/{dummy_id}", response_model=DummyResponse, status_code=status.HTTP_200_OK)
async def update_dummy(
    dummy_update: DummyUpdate,
    dummy: Dummy = Depends(valid_dummy_id),
    db: AsyncSession = Depends(get_db),
):
    return await DummyService.update(dummy_update, dummy, db)


@router.patch("/{dummy_id}", response_model=DummyResponse, status_code=status.HTTP_200_OK)
async def patch_dummy(
    dummy_patch: DummyPatch,
    dummy: Dummy = Depends(valid_dummy_id),
    db: AsyncSession = Depends(get_db),
):
    return await DummyService.patch(dummy_patch, dummy, db)



@router.delete("/{dummy_id}", response_model=DummyDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_dummy(
    dummy: Dummy = Depends(valid_dummy_id),
    db: AsyncSession = Depends(get_db),
):
    return await DummyService.delete(dummy, db)
