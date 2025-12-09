from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..db import models
from ..schemas.guest import GuestCreate, GuestResponse, GuestUpdate
from ..services.guest_service import GuestService
from ..dependencies.security import require_role
from ..core.security import get_current_user
from ..utils.pagination import PaginatedResponse
from ..utils.audit import log_audit

router = APIRouter()

@router.post("/", response_model=GuestResponse)
def create_guest(
    guest_in: GuestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    guest = GuestService.create_guest(db, guest_in)
    
    # Log audit
    log_audit(
        db=db,
        user=current_user,
        action="CREATE",
        entity_type="guest",
        entity_id=guest.id,
        description=f"Created guest {guest.name} {guest.surname}",
        new_values={
            "name": guest.name,
            "surname": guest.surname,
            "email": guest.email,
            "phone_number": guest.phone_number
        },
        request=request
    )
    
    return guest

@router.get("/", response_model=PaginatedResponse[GuestResponse])
def list_guests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return GuestService.list_guests(db, page, page_size, search, sort_by, sort_order)

@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    guest = GuestService.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@router.put("/{guest_id}", response_model=GuestResponse)
def update_guest(
    guest_id: int,
    guest_in: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    guest = GuestService.update_guest(db, guest_id, guest_in)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@router.delete("/{guest_id}", response_model=dict)
def delete_guest(
    guest_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    # Get guest data before deletion for audit log
    guest = GuestService.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    guest_name = f"{guest.name} {guest.surname}"
    old_values = {
        "name": guest.name,
        "surname": guest.surname,
        "email": guest.email,
        "phone_number": guest.phone_number
    }
    
    success = GuestService.delete_guest(db, guest_id)
    
    # Log audit
    log_audit(
        db=db,
        user=current_user,
        action="DELETE",
        entity_type="guest",
        entity_id=guest_id,
        description=f"Deleted guest {guest_name}",
        old_values=old_values,
        request=request
    )
    
    return {"detail": "Guest deleted"}
