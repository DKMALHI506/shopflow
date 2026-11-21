from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order
from app.services.audit_service import record_action


CANCELLABLE_STATUSES = {"pending", "processing"}


def get_customer_order(
    db: Session,
    *,
    order_id: int,
    customer_id: int,
) -> Order:
    statement = select(Order).where(
        Order.id == order_id,
        Order.customer_id == customer_id,
    )
    order = db.scalar(statement)

    # Do not reveal whether an order exists for another customer.
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


def cancel_customer_order(
    db: Session,
    *,
    order_id: int,
    customer_id: int,
    confirm: bool,
) -> dict:
    try:
        order = get_customer_order(
            db,
            order_id=order_id,
            customer_id=customer_id,
        )

        eligible = order.status in CANCELLABLE_STATUSES

        if not confirm:
            return {
                "message": (
                    "This order can be cancelled. Please confirm."
                    if eligible
                    else f"Order cannot be cancelled while its status is '{order.status}'."
                ),
                "eligible": eligible,
                "order": None,
            }

        if not eligible:
            raise HTTPException(
                status_code=409,
                detail=f"Order cannot be cancelled while its status is '{order.status}'.",
            )

        previous_status = order.status
        order.status = "cancelled"

        record_action(
            db,
            entity_type="order",
            entity_id=order.id,
            action="order_cancelled",
            details=f"Order status changed from {previous_status} to cancelled.",
        )

        db.commit()
        db.refresh(order)

        return {
            "message": "Order cancelled successfully.",
            "eligible": True,
            "order": order,
        }

    except Exception:
        db.rollback()
        raise
