from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..db import models
from ..schemas.guest import GuestCreate, GuestUpdate, GuestResponse
from ..services.guest_service import GuestService
from ..dependencies.security import require_role
from ..core.security import get_current_user
from ..utils.pagination import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=GuestResponse)
def create_guest(
    guest_in: GuestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    return GuestService.create_guest(db, guest_in)

@router.get("/", response_model=PaginatedResponse[GuestResponse])
def list_guests(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    success = GuestService.delete_guest(db, guest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"detail": "Guest deleted"}
