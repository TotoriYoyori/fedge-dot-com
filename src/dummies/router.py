from starlette import status
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .dependencies import valid_dummy_id
from .models import Dummy
from .service import DummyService
from .schemas import DummyCreate, DummyUpdate, DummyResponse, DummyPatch, DummyDeleteResponse

# --------------- ROUTING TO http://mysite.com/dummies
router = APIRouter(prefix="/dummies", tags=["dummies"])


@router.post("/", response_model=DummyResponse, status_code=status.HTTP_201_CREATED)
async def create_dummy(
    dummy: DummyCreate,
    db: AsyncSession = Depends(get_db)
):
    return await DummyService.create(dummy, db)


@router.get("/", response_model=list[DummyResponse], status_code=status.HTTP_200_OK)
async def get_all_dummies(
    db: AsyncSession = Depends(get_db)
):
    return await DummyService.get_all(db)


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
