"""
Housekeeping Service
Handles task creation, assignment, updates, and queries
"""
from datetime import datetime, date, time
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from backend.app.db.models import HousekeepingTask, Room, User, Booking, TaskStatus, TaskType, TaskPriority
from backend.app.schemas.housekeeping import (
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    TaskAssignRequest,
    TaskCompletionRequest,
    TaskVerificationRequest,
)
# from backend.app.utils.audit import log_audit  # TODO: Fix audit logging signature


class HousekeepingService:
    """Service for managing housekeeping tasks"""

    def __init__(self, db: Session):
        self.db = db

    def create_task(
        self,
        task_data: HousekeepingTaskCreate,
        created_by_id: int,
    ) -> HousekeepingTask:
        """Create a new housekeeping task"""
        
        # Validate room exists
        room = self.db.query(Room).filter(Room.id == task_data.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {task_data.room_id} not found"
            )

        # If booking_id provided, validate it exists
        if task_data.booking_id:
            booking = self.db.query(Booking).filter(Booking.id == task_data.booking_id).first()
            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Booking {task_data.booking_id} not found"
                )

        # If assigned_to provided, validate user exists
        if task_data.assigned_to:
            user = self.db.query(User).filter(User.id == task_data.assigned_to).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {task_data.assigned_to} not found"
                )

        # Create task
        task = HousekeepingTask(
            room_id=task_data.room_id,
            task_type=task_data.task_type,
            priority=task_data.priority,
            status=TaskStatus.PENDING.value,  # Use .value to get string
            scheduled_date=task_data.scheduled_date,
            scheduled_time=task_data.scheduled_time,
            assigned_to=task_data.assigned_to,
            booking_id=task_data.booking_id,
            notes=task_data.notes,
            created_by=created_by_id,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        # TODO: Add audit logging

        return task

    def get_task(self, task_id: int) -> HousekeepingTask:
        """Get a task by ID"""
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Housekeeping task {task_id} not found"
            )
        return task

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        task_type: Optional[TaskType] = None,
        room_id: Optional[int] = None,
        assigned_to: Optional[int] = None,
        scheduled_date: Optional[date] = None,
        is_overdue: Optional[bool] = None,
    ) -> List[HousekeepingTask]:
        """List tasks with optional filters"""
        
        query = self.db.query(HousekeepingTask)

        # Apply filters
        if status:
            query = query.filter(HousekeepingTask.status == status.value)
        
        if priority:
            query = query.filter(HousekeepingTask.priority == priority.value)
        
        if task_type:
            query = query.filter(HousekeepingTask.task_type == task_type.value)
        
        if room_id:
            query = query.filter(HousekeepingTask.room_id == room_id)
        
        if assigned_to:
            query = query.filter(HousekeepingTask.assigned_to == assigned_to)
        
        if scheduled_date:
            query = query.filter(HousekeepingTask.scheduled_date == scheduled_date)
        
        if is_overdue is not None:
            now = datetime.now()
            today = now.date()
            current_time = now.time()
            
            if is_overdue:
                # Task is overdue if:
                # 1. Scheduled date is before today, OR
                # 2. Scheduled date is today and scheduled_time is before now
                # AND status is not completed or verified
                query = query.filter(
                    and_(
                        HousekeepingTask.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]),
                        or_(
                            HousekeepingTask.scheduled_date < today,
                            and_(
                                HousekeepingTask.scheduled_date == today,
                                HousekeepingTask.scheduled_time < current_time
                            )
                        )
                    )
                )
            else:
                # Not overdue: scheduled date/time is in the future OR already completed/verified
                query = query.filter(
                    or_(
                        HousekeepingTask.status.in_([TaskStatus.COMPLETED.value, TaskStatus.VERIFIED.value]),
                        HousekeepingTask.scheduled_date > today,
                        and_(
                            HousekeepingTask.scheduled_date == today,
                            HousekeepingTask.scheduled_time >= current_time
                        )
                    )
                )

        # Order by priority (urgent > high > normal > low) then scheduled date/time
        from sqlalchemy import case
        priority_order = case(
            (HousekeepingTask.priority == 'urgent', 1),
            (HousekeepingTask.priority == 'high', 2),
            (HousekeepingTask.priority == 'normal', 3),
            (HousekeepingTask.priority == 'low', 4),
            else_=5
        )
        query = query.order_by(
            priority_order,
            HousekeepingTask.scheduled_date,
            HousekeepingTask.scheduled_time
        )

        # Apply pagination
        tasks = query.offset(skip).limit(limit).all()

        return tasks

    def update_task(
        self,
        task_id: int,
        task_data: HousekeepingTaskUpdate,
        updated_by_id: int,
    ) -> HousekeepingTask:
        """Update a housekeeping task"""
        
        task = self.get_task(task_id)

        # Validate assigned_to if being updated
        if task_data.assigned_to is not None:
            user = self.db.query(User).filter(User.id == task_data.assigned_to).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {task_data.assigned_to} not found"
                )

        # Track what changed
        changes = []

        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and getattr(task, field) != value:
                old_value = getattr(task, field)
                setattr(task, field, value)
                changes.append(f"{field}: {old_value} → {value}")

        if not changes:
            return task  # No changes needed

        self.db.commit()
        self.db.refresh(task)

        # TODO: Add audit logging

        return task

    def assign_task(
        self,
        task_id: int,
        assign_data: TaskAssignRequest,
        assigned_by_id: int,
    ) -> HousekeepingTask:
        """Assign task to a staff member"""
        
        task = self.get_task(task_id)

        # Validate user exists
        user = self.db.query(User).filter(User.id == assign_data.assigned_to).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {assign_data.assigned_to} not found"
            )

        task.assigned_to = assign_data.assigned_to
        if assign_data.notes:
            task.notes = (task.notes or "") + f"\n[Assignment] {assign_data.notes}"

        self.db.commit()
        self.db.refresh(task)

        

        return task

    def start_task(
        self,
        task_id: int,
        user_id: int,
    ) -> HousekeepingTask:
        """Mark task as in progress"""
        
        task = self.get_task(task_id)

        # Verify user is assigned to this task
        if task.assigned_to != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this task"
            )

        if task.status != TaskStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start task with status {task.status}"
            )

        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.now()

        self.db.commit()
        self.db.refresh(task)

        

        return task

    def complete_task(
        self,
        task_id: int,
        completion_data: TaskCompletionRequest,
        user_id: int,
    ) -> HousekeepingTask:
        """Mark task as completed"""
        
        task = self.get_task(task_id)

        # Verify user is assigned to this task
        if task.assigned_to != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this task"
            )

        if task.status not in [TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete task with status {task.status}"
            )

        task.status = TaskStatus.COMPLETED.value
        task.completed_at = datetime.now()
        if completion_data.completion_notes:
            task.completion_notes = completion_data.completion_notes

        self.db.commit()
        self.db.refresh(task)

        

        return task

    def verify_task(
        self,
        task_id: int,
        verification_data: TaskVerificationRequest,
        verified_by_id: int,
    ) -> HousekeepingTask:
        """Verify completed task (manager/supervisor only)"""
        
        task = self.get_task(task_id)

        if task.status != TaskStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only verify completed tasks, current status: {task.status}"
            )

        task.status = TaskStatus.VERIFIED.value
        task.verified_by = verified_by_id
        task.verified_at = datetime.now()
        if verification_data.verification_notes:
            task.verification_notes = verification_data.verification_notes

        self.db.commit()
        self.db.refresh(task)

        
        return task

    def delete_task(
        self,
        task_id: int,
        deleted_by_id: int,
    ) -> None:
        """Delete a housekeeping task"""
        
        task = self.get_task(task_id)

        # Only allow deletion of pending tasks
        if task.status != TaskStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete task with status {task.status}"
            )

        

        self.db.delete(task)
        self.db.commit()
