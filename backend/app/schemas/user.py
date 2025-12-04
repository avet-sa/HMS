from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    permission_level: Optional[str] = "REGULAR"


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    permission_level: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    permission_level: str
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
