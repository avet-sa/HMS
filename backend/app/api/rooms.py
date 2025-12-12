from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..db import models
from ..schemas.room import RoomCreate, RoomUpdate, RoomResponse
from ..services.room_service import RoomService
from ..dependencies.security import require_role
from ..core.security import get_current_user
from ..utils.pagination import paginate, apply_sorting, PaginatedResponse
from ..utils.audit import log_audit

router = APIRouter()

@router.post("/", response_model=RoomResponse)
def create_room(
    room_in: RoomCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    room = RoomService.create_room(db, room_in)
    
    # Log audit
    log_audit(
        db=db,
        user=current_user,
        action="CREATE",
        entity_type="room",
        entity_id=room.id,
        description=f"Created room {room.number}",
        new_values={
            "number": room.number,
            "room_type_id": room.room_type_id,
            "price_per_night": str(room.price_per_night),
            "maintenance_status": room.maintenance_status.value if room.maintenance_status else None
        },
        request=request
    )
    
    return room

@router.get("/", response_model=PaginatedResponse[RoomResponse])
def list_rooms(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type"),
    search: Optional[str] = Query(None, description="Search by room number"),
    sort_by: Optional[str] = Query(None, description="Sort by field (e.g., number, price_per_night)"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return RoomService.list_rooms(db, page, page_size, status, room_type_id, search, sort_by, sort_order)

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_in: RoomUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    # Get old room data for audit log
    old_room = RoomService.get_room(db, room_id)
    if not old_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    old_values = {
        "price_per_night": str(old_room.price_per_night),
        "maintenance_status": old_room.maintenance_status.value if old_room.maintenance_status else None
    }
    
    room = RoomService.update_room(db, room_id, room_in)
    
    new_values = {
        "price_per_night": str(room.price_per_night),
        "maintenance_status": room.maintenance_status.value if room.maintenance_status else None
    }
    
    # Log audit
    log_audit(
        db=db,
        user=current_user,
        action="UPDATE",
        entity_type="room",
        entity_id=room.id,
        description=f"Updated room {room.number}",
        old_values=old_values,
        new_values=new_values,
        request=request
    )
    
    return room

@router.delete("/{room_id}", response_model=dict)
def delete_room(
    room_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    # Get room data before deletion for audit log
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_number = room.number
    old_values = {
        "number": room.number,
        "room_type_id": room.room_type_id,
        "price_per_night": str(room.price_per_night)
    }
    
    success = RoomService.delete_room(db, room_id)
    
    # Log audit
    log_audit(
        db=db,
        user=current_user,
        action="DELETE",
        entity_type="room",
        entity_id=room_id,
        description=f"Deleted room {room_number}",
        old_values=old_values,
        request=request
    )
    
    return {"detail": "Room deleted"}
