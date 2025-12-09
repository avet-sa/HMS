from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from ..db.session import get_db
from ..schemas.user import UserResponse, UserCreate, UserUpdate
from ..services.user_service import UserService
from ..core.security import get_current_user
from ..dependencies.security import require_role
from ..db import models
from ..utils.audit import log_audit

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    """List all users (admin only)."""
    return db.query(models.User).all()


@router.post("/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    """Create a new user (admin only)."""
    # Check if username already exists
    existing = UserService.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    new_user = UserService.create_user(db, user_in)
    
    # Log user creation
    log_audit(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="user",
        entity_id=new_user.id,
        description=f"Created user: {new_user.username}",
        new_values={
            "username": new_user.username,
            "permission_level": new_user.permission_level.value,
            "is_active": new_user.is_active
        },
        request=request
    )
    
    return new_user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    """Update a user (admin only)."""
    # Get old values before update
    old_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not old_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    old_values = {}
    new_values = {}
    
    if user_in.permission_level and user_in.permission_level != old_user.permission_level:
        old_values["permission_level"] = old_user.permission_level.value
        new_values["permission_level"] = user_in.permission_level.value
    
    if user_in.is_active is not None and user_in.is_active != old_user.is_active:
        old_values["is_active"] = old_user.is_active
        new_values["is_active"] = user_in.is_active
    
    user = UserService.update_user(db, user_id, user_in)
    
    # Log user update
    if old_values or new_values:
        log_audit(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            entity_type="user",
            entity_id=user.id,
            description=f"Updated user: {user.username}",
            old_values=old_values if old_values else None,
            new_values=new_values if new_values else None,
            request=request
        )
    
    return user


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    """Deactivate a user (admin only). Cannot deactivate yourself."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself"
        )
    user = UserService.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Log user deactivation
    log_audit(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="user",
        entity_id=user.id,
        description=f"Deactivated user: {user.username}",
        old_values={"is_active": True},
        new_values={"is_active": False},
        request=request
    )
    
    return user
