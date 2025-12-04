from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db.session import get_db
from ..schemas.room import RoomCreate, RoomUpdate, RoomResponse
from ..services.room_service import RoomService

router = APIRouter()

@router.post("/", response_model=RoomResponse)
def create_room(room_in: RoomCreate, db: Session = Depends(get_db)):
    return RoomService.create_room(db, room_in)

@router.get("/", response_model=List[RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    return RoomService.list_rooms(db)

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room_in: RoomUpdate, db: Session = Depends(get_db)):
    room = RoomService.update_room(db, room_id, room_in)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/{room_id}", response_model=dict)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    success = RoomService.delete_room(db, room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"detail": "Room deleted"}
