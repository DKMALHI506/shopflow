from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer, Order, Ticket
from app.schemas import TicketCreate, TicketResponse
from app.services.audit_service import record_action

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    customer = db.get(Customer, payload.customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.order_id is not None:
        order = db.scalar(
            select(Order).where(
                Order.id == payload.order_id,
                Order.customer_id == payload.customer_id,
            )
        )
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found for this customer",
            )

    ticket = Ticket(
        customer_id=payload.customer_id,
        order_id=payload.order_id,
        subject=payload.subject.strip(),
        description=payload.description.strip(),
        priority=payload.priority,
    )

    try:
        db.add(ticket)
        db.flush()

        record_action(
            db,
            entity_type="ticket",
            entity_id=ticket.id,
            action="ticket_created",
            details=f"Ticket created with priority '{ticket.priority}'.",
        )

        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise

    return ticket
