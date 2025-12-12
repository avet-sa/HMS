from pydantic import BaseModel
from datetime import date
from typing import List, Dict
from decimal import Decimal


class TaskStatusCount(BaseModel):
    """Count of tasks by status"""
    status: str
    count: int


class TaskPriorityCount(BaseModel):
    """Count of tasks by priority"""
    priority: str
    count: int


class StaffPerformance(BaseModel):
    """Performance metrics for a staff member"""
    user_id: int
    username: str
    tasks_completed: int
    tasks_verified: int
    average_duration_minutes: Decimal
    total_hours_worked: Decimal


class RoomStatusInfo(BaseModel):
    """Status information for a single room"""
    room_id: int
    room_number: str
    room_type: str
    maintenance_status: str
    has_pending_tasks: bool
    has_in_progress_tasks: bool
    next_booking_checkin: date | None


class HousekeepingDashboard(BaseModel):
    """Dashboard statistics for housekeeping overview"""
    # Task counts by status
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    verified_tasks: int
    
    # Task counts by priority
    urgent_tasks: int
    high_priority_tasks: int
    normal_priority_tasks: int
    low_priority_tasks: int
    
    # Today's metrics
    tasks_scheduled_today: int
    tasks_completed_today: int
    checkout_cleanings_pending: int
    
    # Room status summary
    rooms_available: int
    rooms_in_maintenance: int
    rooms_out_of_service: int
    
    # Recent activity
    tasks_by_status: List[TaskStatusCount]
    tasks_by_priority: List[TaskPriorityCount]


class StaffPerformanceReport(BaseModel):
    """Staff performance report with date range"""
    start_date: date
    end_date: date
    staff_metrics: List[StaffPerformance]
    total_tasks_completed: int
    total_tasks_verified: int
    average_completion_time_minutes: Decimal


class RoomStatusGrid(BaseModel):
    """Grid view of all rooms with their housekeeping status"""
    as_of_date: date
    rooms: List[RoomStatusInfo]
    summary: Dict[str, int]  # Status -> count mapping
