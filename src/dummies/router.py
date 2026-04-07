from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dummies.dependencies import valid_dummy_id
from src.dummies.service import DummyService
from src.dummies.schemas import DummyCreate, DummyResponse


router = APIRouter(prefix="/dummies", tags=["dummies"])

@router.get('/', response_model=list[DummyResponse])
async def get_all_dummies(db: AsyncSession = Depends(get_db)):
    return await DummyService.get_all(db)

@router.get('/{order_id}', response_model=DummyResponse)
async def get_dummy(dummy: DummyResponse = Depends(valid_dummy_id)):
    return dummy

@router.post('/', response_model=DummyResponse, status_code=201)
async def create_dummy(dummy: DummyCreate, db: AsyncSession = Depends(get_db)):
    return await DummyService.create(db, dummy)