# ----- Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# ----- Local Modules
from src.database import get_db
from src.orders.dependencies import valid_order_id
from src.orders.service import OrderService
from src.orders.schemas import OrderCreate, OrderResponse

# ----- API Routes
router = APIRouter(prefix="/orders", tags=["orders"])

@router.get('/', response_model=list[OrderResponse])
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    return await OrderService.get_all(db)

@router.get('/{order_id}', response_model=OrderResponse)
async def get_order(order: OrderResponse = Depends(valid_order_id)):
    return order

@router.post('/', response_model=OrderResponse, status_code=201)
async def create_order(order: DummyCreate, db: AsyncSession = Depends(get_db)):
    return await OrderService.create(db, order)