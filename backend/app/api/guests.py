from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.session import get_db
from ..db import models
from ..schemas.guest import GuestCreate, GuestUpdate, GuestResponse
from ..services.guest_service import GuestService
from ..dependencies.security import require_role
from ..core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=GuestResponse)
def create_guest(
    guest_in: GuestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    return GuestService.create_guest(db, guest_in)

@router.get("/", response_model=List[GuestResponse])
def list_guests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return GuestService.list_guests(db)

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
