from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_role
from src.auth.models import User
from src.database import get_db
from src.google.dependencies import valid_google_oauth_credential
from src.google.models import GoogleOAuthCredential
from src.orders.schemas import OrdersFetchResponse, OrdersListResponse
from src.orders.service import fetch_and_persist_benify_orders, list_persisted_orders


router = APIRouter(prefix="/api/v1/orders", tags=["api-orders"])


@router.post("/", response_model=OrdersFetchResponse)
async def fetch_orders(
    record: Annotated[GoogleOAuthCredential, Depends(valid_google_oauth_credential)],
    max_results: int = Query(default=5, ge=1, le=100),
    label: str | None = Query(default=None),
    after: date | None = Query(default=None),
    before: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    return await fetch_and_persist_benify_orders(
        db=db,
        record=record,
        max_results=max_results,
        label=label,
        after=after,
        before=before,
    )


@router.get("/", response_model=OrdersListResponse)
async def get_all_orders(
    valid_user: Annotated[User, Depends(require_role("merchant", "admin"))],
    db: AsyncSession = Depends(get_db),
):
    return await list_persisted_orders(db=db, merchant_id=valid_user.id)
