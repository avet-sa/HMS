from uuid import uuid4

from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from fastapi import HTTPException

from ..db import models
from ..utils.availability import is_room_available
from ..schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    # Valid state transitions
    VALID_TRANSITIONS = {
        models.BookingStatus.PENDING: [models.BookingStatus.CONFIRMED, models.BookingStatus.CANCELLED],
        models.BookingStatus.CONFIRMED: [models.BookingStatus.CHECKED_IN, models.BookingStatus.CANCELLED, models.BookingStatus.NO_SHOW],
        models.BookingStatus.CHECKED_IN: [models.BookingStatus.CHECKED_OUT],
        models.BookingStatus.CHECKED_OUT: [],
        models.BookingStatus.CANCELLED: [],
        models.BookingStatus.NO_SHOW: [],
    }

    @staticmethod
    def _validate_transition(from_status: models.BookingStatus, to_status: models.BookingStatus):
        """Validate if transition is allowed."""
        if to_status not in BookingService.VALID_TRANSITIONS.get(from_status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transition from {from_status.value} to {to_status.value}"
            )

    # noinspection PyTypeChecker
    @staticmethod
    def create_booking(db: Session, data: BookingCreate, created_by_user_id: int = None) -> models.Booking:
        # Check room availability
        if not is_room_available(db, data.room_id, data.check_in, data.check_out):
            raise ValueError("Room is not available for the selected dates.")

        room = db.query(models.Room).filter(models.Room.id == data.room_id).first()
        if not room:
            raise ValueError("Room not found.")

        # Freeze price at booking time
        price_per_night = room.price_per_night

        # Calculate total price
        nights = (data.check_out - data.check_in).days
        total_price = nights * price_per_night

        # Generate booking number if not provided
        booking_number = f"BK-{uuid4().hex[:8].upper()}"

        booking = models.Booking(
            booking_number=booking_number,
            room_id=data.room_id,
            guest_id=data.guest_id,
            created_by=created_by_user_id,
            check_in=data.check_in,
            check_out=data.check_out,
            number_of_guests=data.number_of_guests,
            price_per_night=price_per_night,
            total_price=total_price,
            status=models.BookingStatus.PENDING.value,
            special_requests=data.special_requests,
            internal_notes=data.internal_notes,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_booking(db: Session, booking_id: int) -> models.Booking | None:
        return (
            db.query(models.Booking).
            options(joinedload(models.Booking.guest))
            .filter(models.Booking.id == booking_id)
            .first()
        )

    @staticmethod
    def list_bookings(db: Session, current_user: models.User = None):
        """
        List bookings with role-based filtering:
        - ADMIN, MANAGER: see all bookings
        - REGULAR: see only own bookings (created_by == user.id)
        """
        query = db.query(models.Booking).options(joinedload(models.Booking.guest))
        
        # Filter by role
        if current_user and current_user.permission_level == models.PermissionLevel.REGULAR:
            query = query.filter(models.Booking.created_by == current_user.id)
        
        return query.all()

    @staticmethod
    def update_booking(db: Session, booking_id: int, data: BookingUpdate):
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None

        # If dates changed → check availability
        if data.check_in or data.check_out:
            if not is_room_available(
                db,
                booking.room_id,
                data.check_in or booking.check_in,
                data.check_out or booking.check_out,
                exclude_booking_id=booking_id,
            ):
                raise ValueError("Room is not available for updated dates.")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(booking, field, value)

        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def confirm_booking(db: Session, booking_id: int):
        """Transition from PENDING to CONFIRMED."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.CONFIRMED)
        
        booking.status = models.BookingStatus.CONFIRMED.value
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def check_in_booking(db: Session, booking_id: int):
        """Transition from CONFIRMED to CHECKED_IN."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.CHECKED_IN)
        
        booking.status = models.BookingStatus.CHECKED_IN.value
        booking.actual_check_in = datetime.now()
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def check_out_booking(db: Session, booking_id: int):
        """Transition from CHECKED_IN to CHECKED_OUT."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.CHECKED_OUT)
        
        booking.status = models.BookingStatus.CHECKED_OUT.value
        booking.actual_check_out = datetime.now()
        
        # Calculate final bill based on actual nights
        if booking.actual_check_in:
            actual_nights = (booking.actual_check_out - booking.actual_check_in).days
            booking.final_bill = actual_nights * booking.price_per_night
        
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def cancel_booking(db: Session, booking_id: int):
        """Transition from PENDING/CONFIRMED to CANCELLED."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.CANCELLED)
        
        booking.status = models.BookingStatus.CANCELLED.value
        booking.cancelled_at = datetime.now()
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def mark_no_show(db: Session, booking_id: int):
        """Transition from CONFIRMED to NO_SHOW."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.NO_SHOW)
        
        booking.status = models.BookingStatus.NO_SHOW.value
        db.commit()
        db.refresh(booking)
        return booking
