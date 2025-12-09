"""
Pydantic schemas for audit logs
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    """Base audit log schema"""
    pass


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log (internal use)"""
    user_id: Optional[int] = None
    username: str
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    description: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response"""
    id: int
    user_id: Optional[int]
    username: str
    action: str
    entity_type: str
    entity_id: Optional[int]
    description: Optional[str]
    old_values: Optional[str]
    new_values: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
