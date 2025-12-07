from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import datetime


class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal
    method: str
    currency: Optional[str] = "USD"


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    currency: str
    method: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    reference: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
