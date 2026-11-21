from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer
from app.schemas import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
) -> Customer:
    email = str(payload.email).lower()
    existing = db.scalar(
        select(Customer).where(Customer.email == email)
    )

    if existing:
        raise HTTPException(status_code=409, detail="Customer already exists")

    customer = Customer(name=payload.name.strip(), email=email)
    db.add(customer)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Customer already exists")

    return customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
) -> Customer:
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer
