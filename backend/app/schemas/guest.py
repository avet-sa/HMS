from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime


class GuestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    nationality: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    document_type: Optional[str] = Field(None, max_length=20)
    document_id: Optional[str] = Field(None, max_length=50)
    loyalty_points: Optional[int] = 0
    vip_tier: Optional[int] = 0
    is_active: Optional[bool] = True


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=30)
    email: Optional[EmailStr] = None
    nationality: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    document_type: Optional[str] = Field(None, max_length=20)
    document_id: Optional[str] = Field(None, max_length=50)
    loyalty_points: Optional[int] = None
    vip_tier: Optional[int] = None
    is_active: Optional[bool] = None


class GuestResponse(GuestBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
