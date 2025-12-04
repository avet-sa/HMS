from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date, datetime


class BookingBase(BaseModel):
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    number_of_guests: int = Field(1, ge=1)
    number_of_nights: int = Field(..., ge=1)
    price_per_night: Decimal
    total_price: Decimal
    status: Optional[str] = "pending"
    special_requests: Optional[str] = Field(None, max_length=500)
    internal_notes: Optional[str] = Field(None, max_length=500)


class BookingCreate(BookingBase):
    booking_number: Optional[str] = Field(None, max_length=20)  # server can generate if not provided


class BookingUpdate(BaseModel):
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    number_of_guests: Optional[int] = Field(None, ge=1)
    number_of_nights: Optional[int] = Field(None, ge=1)
    price_per_night: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    status: Optional[str] = None
    special_requests: Optional[str] = Field(None, max_length=500)
    internal_notes: Optional[str] = Field(None, max_length=500)


class BookingResponse(BookingBase):
    id: int
    booking_number: str
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
