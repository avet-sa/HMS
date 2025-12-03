from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.guest import GuestCreate, GuestUpdate, GuestResponse
from app.services.guest_service import GuestService

router = APIRouter()

@router.post("/", response_model=GuestResponse)
def create_guest(guest_in: GuestCreate, db: Session = Depends(get_db)):
    return GuestService.create_guest(db, guest_in)

@router.get("/", response_model=List[GuestResponse])
def list_guests(db: Session = Depends(get_db)):
    return GuestService.list_guests(db)

@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = GuestService.get_guest(db, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@router.put("/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, guest_in: GuestUpdate, db: Session = Depends(get_db)):
    guest = GuestService.update_guest(db, guest_id, guest_in)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@router.delete("/{guest_id}", response_model=dict)
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    success = GuestService.delete_guest(db, guest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"detail": "Guest deleted"}
