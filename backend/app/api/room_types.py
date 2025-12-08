from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.session import get_db
from ..db import models
from ..schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from ..dependencies.security import require_role
from ..core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=RoomTypeResponse)
def create_room_type(
    room_type_in: RoomTypeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    room_type = models.RoomType(
        name=room_type_in.name,
        base_price=room_type_in.base_price,
        capacity=room_type_in.capacity,
        description=room_type_in.description
    )
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type

@router.get("/", response_model=List[RoomTypeResponse])
def list_room_types(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.RoomType).all()

@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    room_type = db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    return room_type

@router.put("/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(
    room_type_id: int,
    room_type_in: RoomTypeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    room_type = db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    
    for field, value in room_type_in.model_dump(exclude_unset=True).items():
        setattr(room_type, field, value)
    
    db.commit()
    db.refresh(room_type)
    return room_type

@router.delete("/{room_type_id}", response_model=dict)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    room_type = db.query(models.RoomType).filter(models.RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found")
    
    db.delete(room_type)
    db.commit()
    return {"detail": "Room type deleted"}
