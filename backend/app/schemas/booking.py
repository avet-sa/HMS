from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, validator
from decimal import Decimal
from datetime import date, datetime


class BookingBase(BaseModel):
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    number_of_guests: int = Field(1, ge=1)
    status: Optional[str] = "pending"
    special_requests: Optional[str] = Field(None, max_length=500)
    internal_notes: Optional[str] = Field(None, max_length=500)


class BookingCreate(BookingBase):
    booking_number: Optional[str] = Field(None, max_length=20)  # server can generate if not provided

class GuestBasic(BaseModel):
    id: int
    name: str
    surname: str
    model_config = ConfigDict(from_attributes=True)

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


# class BookingResponse(BookingBase):
#     id: int
#     booking_number: str
#     created_at: datetime
#     updated_at: Optional[datetime]
#     model_config = ConfigDict(from_attributes=True)

class BookingResponse(BaseModel):
    id: int
    booking_number: str
    guest: GuestBasic       # ← instead of guest_id
    room_id: int
    check_in: date
    check_out: date
    number_of_guests: int
    number_of_nights: int
    price_per_night: float
    total_price: float
    status: str
    special_requests: str | None
    internal_notes: str | None
    created_at: datetime
    updated_at: datetime | None
    model_config = ConfigDict(from_attributes=True)