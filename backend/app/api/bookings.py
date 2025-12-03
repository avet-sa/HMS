from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.services.booking_service import BookingService

router = APIRouter()

@router.post("/", response_model=BookingResponse)
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    try:
        return BookingService.create_booking(db, booking_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[BookingResponse])
def list_bookings(db: Session = Depends(get_db)):
    return BookingService.list_bookings(db)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, booking_in: BookingUpdate, db: Session = Depends(get_db)):
    try:
        booking = BookingService.update_booking(db, booking_id, booking_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("/{booking_id}/checkin", response_model=BookingResponse)
def check_in(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.check_in(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("/{booking_id}/checkout", response_model=BookingResponse)
def check_out(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.check_out(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = BookingService.cancel_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
