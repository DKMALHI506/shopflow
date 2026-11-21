from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    total: Decimal
    tracking_number: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CancelOrderRequest(BaseModel):
    # Development-only identity field. Replace with authenticated identity later.
    customer_id: int = Field(gt=0)
    confirm: bool = False


class CancelOrderResponse(BaseModel):
    message: str
    eligible: bool
    order: OrderResponse | None = None


class TicketCreate(BaseModel):
    customer_id: int = Field(gt=0)
    order_id: int | None = Field(default=None, gt=0)
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5, max_length=5000)
    priority: Literal["low", "normal", "high"] = "normal"


class TicketResponse(BaseModel):
    id: int
    customer_id: int
    order_id: int | None
    subject: str
    description: str
    status: str
    priority: str

    model_config = ConfigDict(from_attributes=True)
