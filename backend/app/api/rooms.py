from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..db import models
from ..schemas.room import RoomCreate, RoomUpdate, RoomResponse
from ..services.room_service import RoomService
from ..dependencies.security import require_role
from ..core.security import get_current_user
from ..utils.pagination import paginate, apply_sorting, PaginatedResponse

router = APIRouter()

@router.post("/", response_model=RoomResponse)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    return RoomService.create_room(db, room_in)

@router.get("/", response_model=PaginatedResponse[RoomResponse])
def list_rooms(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    room_type_id: Optional[int] = Query(None, description="Filter by room type"),
    sort_by: Optional[str] = Query(None, description="Sort by field (e.g., number, price_per_night)"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return RoomService.list_rooms(db, page, page_size, status, room_type_id, sort_by, sort_order)

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    room = RoomService.update_room(db, room_id, room_in)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/{room_id}", response_model=dict)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    success = RoomService.delete_room(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"detail": "Room deleted"}
