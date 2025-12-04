from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class PaymentBase(BaseModel):
    booking_id: int
    amount: Decimal
    payment_method: str
    payment_status: Optional[str] = "pending"
    transaction_id: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=255)


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    transaction_id: Optional[str] = Field(None, max_length=100)
    payment_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=255)


class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
