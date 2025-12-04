from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class RoomBase(BaseModel):
    number: str = Field(..., min_length=1, max_length=10)
    room_type_id: int
    price_per_night: Decimal
    square_meters: Optional[int]
    floor: Optional[int]
    maintenance_status: Optional[str] = "available"
    has_view: Optional[bool] = False
    is_smoking: Optional[bool] = False


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    number: Optional[str] = Field(None, max_length=10)
    room_type_id: Optional[int] = None
    price_per_night: Optional[Decimal] = None
    square_meters: Optional[int] = None
    floor: Optional[int] = None
    maintenance_status: Optional[str] = None
    has_view: Optional[bool] = None
    is_smoking: Optional[bool] = None


class RoomResponse(RoomBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
