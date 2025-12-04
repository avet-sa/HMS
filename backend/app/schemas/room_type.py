from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class RoomTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    base_price: Decimal
    capacity: int
    description: Optional[str] = Field(None, max_length=500)


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    base_price: Optional[Decimal] = None
    capacity: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)


class RoomTypeResponse(RoomTypeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
