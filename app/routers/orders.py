from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CancelOrderRequest,
    CancelOrderResponse,
    OrderResponse,
)
from app.services.order_service import (
    cancel_customer_order,
    get_customer_order,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    customer_id: int,
    db: Session = Depends(get_db),
):
    return get_customer_order(
        db,
        order_id=order_id,
        customer_id=customer_id,
    )


@router.post("/{order_id}/cancel", response_model=CancelOrderResponse)
def cancel_order(
    order_id: int,
    payload: CancelOrderRequest,
    db: Session = Depends(get_db),
):
    return cancel_customer_order(
        db,
        order_id=order_id,
        customer_id=payload.customer_id,
        confirm=payload.confirm,
    )
