"""
Housekeeping API endpoints
CRUD operations and workflow actions for housekeeping tasks
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import User, TaskStatus, TaskType, TaskPriority, PermissionLevel
from backend.app.core.security import get_current_user
from backend.app.dependencies.security import require_role
from backend.app.schemas.housekeeping import (
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    HousekeepingTaskResponse,
    TaskAssignRequest,
    TaskCompletionRequest,
    TaskVerificationRequest,
)
from backend.app.services.housekeeping_service import HousekeepingService


router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])


@router.post(
    "/tasks/",
    response_model=HousekeepingTaskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN))],
)
def create_housekeeping_task(
    task_data: HousekeepingTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new housekeeping task (Manager+ only)
    """
    service = HousekeepingService(db)
    return service.create_task(task_data, created_by_id=current_user.id)


@router.get("/tasks/", response_model=List[HousekeepingTaskResponse])
def list_housekeeping_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    task_type: Optional[TaskType] = None,
    room_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    scheduled_date: Optional[date] = None,
    is_overdue: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List housekeeping tasks with filters
    
    - Staff can only see tasks assigned to them
    - Managers+ can see all tasks
    """
    service = HousekeepingService(db)
    
    # If user is staff (not manager/admin), only show their assigned tasks
    if current_user.permission_level == PermissionLevel.REGULAR:
        assigned_to = current_user.id
    
    return service.list_tasks(
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        task_type=task_type,
        room_id=room_id,
        assigned_to=assigned_to,
        scheduled_date=scheduled_date,
        is_overdue=is_overdue,
    )


@router.get("/tasks/{task_id}", response_model=HousekeepingTaskResponse)
def get_housekeeping_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific housekeeping task by ID
    
    - Staff can only view tasks assigned to them
    - Managers+ can view any task
    """
    service = HousekeepingService(db)
    task = service.get_task(task_id)
    
    # Check permissions
    if current_user.permission_level == PermissionLevel.REGULAR:
        if task.assigned_to != current_user.id:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view tasks assigned to you"
            )
    
    return task


@router.patch(
    "/tasks/{task_id}",
    response_model=HousekeepingTaskResponse,
    dependencies=[Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN))],
)
def update_housekeeping_task(
    task_id: int,
    task_data: HousekeepingTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a housekeeping task (Manager+ only)
    """
    service = HousekeepingService(db)
    return service.update_task(task_id, task_data, updated_by_id=current_user.id)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN))],
)
def delete_housekeeping_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a housekeeping task (Manager+ only)
    
    Only pending tasks can be deleted
    """
    service = HousekeepingService(db)
    service.delete_task(task_id, deleted_by_id=current_user.id)


# ============================================================================
# WORKFLOW ACTIONS
# ============================================================================

@router.post(
    "/tasks/{task_id}/assign",
    response_model=HousekeepingTaskResponse,
    dependencies=[Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN))],
)
def assign_housekeeping_task(
    task_id: int,
    assign_data: TaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign task to a staff member (Manager+ only)
    """
    service = HousekeepingService(db)
    return service.assign_task(task_id, assign_data, assigned_by_id=current_user.id)


@router.post(
    "/tasks/{task_id}/start",
    response_model=HousekeepingTaskResponse,
)
def start_housekeeping_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start working on a task (assigned staff only)
    
    Must be assigned to the task
    """
    service = HousekeepingService(db)
    return service.start_task(task_id, user_id=current_user.id)


@router.post(
    "/tasks/{task_id}/complete",
    response_model=HousekeepingTaskResponse,
)
def complete_housekeeping_task(
    task_id: int,
    completion_data: TaskCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark task as completed (assigned staff only)
    
    Must be assigned to the task
    """
    service = HousekeepingService(db)
    return service.complete_task(task_id, completion_data, user_id=current_user.id)


@router.post(
    "/tasks/{task_id}/verify",
    response_model=HousekeepingTaskResponse,
    dependencies=[Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN))],
)
def verify_housekeeping_task(
    task_id: int,
    verification_data: TaskVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Verify completed task (Manager+ only)
    
    Task must be in COMPLETED status
    """
    service = HousekeepingService(db)
    return service.verify_task(task_id, verification_data, verified_by_id=current_user.id)
