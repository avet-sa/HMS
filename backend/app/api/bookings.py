from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from backend.app.db.session import get_db
from backend.app.db import models
from backend.app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from backend.app.services.booking_service import BookingService
from backend.app.dependencies.security import require_role
from backend.app.core.security import get_current_user
from backend.app.utils.pagination import PaginatedResponse
from backend.app.utils.audit import log_booking_action

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    booking_in: BookingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        booking = BookingService.create_booking(db, booking_in, created_by_user_id=current_user.id)
        
        # Log audit
        log_booking_action(
            db=db,
            user=current_user,
            action="CREATE",
            booking_id=booking.id,
            description=f"Created booking #{booking.booking_number} for guest ID {booking.guest_id}",
            new_values={
                "booking_number": booking.booking_number,
                "guest_id": booking.guest_id,
                "room_id": booking.room_id,
                "check_in": str(booking.check_in),
                "check_out": str(booking.check_out),
                "status": booking.status.value
            },
            request=request
        )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=PaginatedResponse[BookingResponse])
def list_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    check_in_from: Optional[date] = Query(None, description="Filter check-in from date"),
    check_in_to: Optional[date] = Query(None, description="Filter check-in to date"),
    search: Optional[str] = Query(None, description="Search by guest name or booking number"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return BookingService.list_bookings(db, current_user, page, page_size, status, check_in_from, check_in_to, search, sort_by, sort_order)

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check access: ADMIN/MANAGER see all, REGULAR see only own
    if current_user.permission_level == models.PermissionLevel.REGULAR and booking.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot view this booking")
    
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        booking = BookingService.update_booking(db, booking_id, booking_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}", response_model=dict)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN))
):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"detail": "Booking deleted"}

@router.post("/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        booking = BookingService.confirm_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except HTTPException as e:
        raise e

@router.post("/{booking_id}/check-in", response_model=BookingResponse)
def check_in(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        booking = BookingService.check_in_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Log audit
        log_booking_action(
            db=db,
            user=current_user,
            action="CHECK_IN",
            booking_id=booking.id,
            description=f"Guest checked in for booking #{booking.booking_number}",
            new_values={"status": booking.status.value},
            request=request
        )
        
        return booking
    except HTTPException as e:
        raise e

@router.post("/{booking_id}/check-out", response_model=BookingResponse)
def check_out(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        booking = BookingService.check_out_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Log audit
        log_booking_action(
            db=db,
            user=current_user,
            action="CHECK_OUT",
            booking_id=booking.id,
            description=f"Guest checked out for booking #{booking.booking_number}",
            new_values={"status": booking.status.value},
            request=request
        )
        
        return booking
    except HTTPException as e:
        raise e

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # RBAC: REGULAR users can only cancel their own bookings
        if current_user.permission_level == models.PermissionLevel.REGULAR:
            if booking.created_by != current_user.id:
                raise HTTPException(status_code=403, detail="You can only cancel your own bookings")
        
        old_status = booking.status.value
        booking = BookingService.cancel_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Log audit
        log_booking_action(
            db=db,
            user=current_user,
            action="CANCEL",
            booking_id=booking.id,
            description=f"Cancelled booking #{booking.booking_number}",
            old_values={"status": old_status},
            new_values={"status": booking.status.value},
            request=request
        )
        
        return booking
    except HTTPException as e:
        raise e

@router.post("/{booking_id}/no-show", response_model=BookingResponse)
def mark_no_show(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        booking = BookingService.mark_no_show(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except HTTPException as e:
        raise e
