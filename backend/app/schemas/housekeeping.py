"""
Pydantic schemas for Housekeeping Tasks
"""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import date, datetime, time


class HousekeepingTaskBase(BaseModel):
    """Base schema for housekeeping task"""
    room_id: int
    task_type: str  # cleaning, maintenance, inspection, deep_cleaning, turndown
    priority: str = "normal"  # low, normal, high, urgent
    scheduled_date: date
    scheduled_time: Optional[str] = None  # HH:MM format
    notes: Optional[str] = None
    estimated_duration_minutes: int = 30
    assigned_to: Optional[int] = None
    booking_id: Optional[int] = None
    is_checkout_cleaning: bool = False
    
    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        valid_types = ["cleaning", "maintenance", "inspection", "deep_cleaning", "turndown"]
        if v not in valid_types:
            raise ValueError(f"task_type must be one of {valid_types}")
        return v
    
    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"priority must be one of {valid_priorities}")
        return v
    
    @field_validator("scheduled_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                # Validate HH:MM format
                hours, minutes = v.split(":")
                if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
                    raise ValueError
            except (ValueError, AttributeError):
                raise ValueError("scheduled_time must be in HH:MM format (e.g., '14:30')")
        return v


class HousekeepingTaskCreate(HousekeepingTaskBase):
    """Schema for creating a housekeeping task"""
    pass


class HousekeepingTaskUpdate(BaseModel):
    """Schema for updating a housekeeping task"""
    room_id: Optional[int] = None
    task_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    assigned_to: Optional[int] = None
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_statuses = ["pending", "in_progress", "completed", "verified", "failed"]
            if v not in valid_statuses:
                raise ValueError(f"status must be one of {valid_statuses}")
        return v


class HousekeepingTaskResponse(HousekeepingTaskBase):
    """Schema for housekeeping task response"""
    id: int
    status: str
    created_by: int
    verified_by: Optional[int] = None
    is_checkout_cleaning: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    verification_notes: Optional[str] = None
    actual_duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskAssignRequest(BaseModel):
    """Schema for assigning a task to a user"""
    assigned_to: int
    notes: Optional[str] = None


class TaskCompletionRequest(BaseModel):
    """Schema for completing a task"""
    completion_notes: Optional[str] = None


class TaskVerificationRequest(BaseModel):
    """Schema for verifying a completed task"""
    verification_notes: Optional[str] = None


class HousekeepingDashboard(BaseModel):
    """Schema for housekeeping dashboard statistics"""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    verified_tasks: int
    overdue_tasks: int
    rooms_needing_cleaning: int
    avg_completion_time_minutes: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class StaffPerformance(BaseModel):
    """Schema for staff performance metrics"""
    user_id: int
    username: str
    total_tasks: int
    completed_tasks: int
    verified_tasks: int
    avg_completion_time_minutes: Optional[float] = None
    completion_rate: float
    verification_rate: float
    
    model_config = ConfigDict(from_attributes=True)
