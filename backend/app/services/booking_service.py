from uuid import uuid4

from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException

from ..db import models
from ..utils.availability import is_room_available
from ..utils.pagination import paginate, apply_sorting
from ..schemas.booking import BookingCreate, BookingUpdate
from .refund_policy import RefundPolicyService


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
    def list_bookings(db: Session, current_user: models.User = None, page: int = 1, page_size: int = 50,
                     status: Optional[str] = None, check_in_from: Optional[date] = None,
                     check_in_to: Optional[date] = None, sort_by: Optional[str] = None, sort_order: str = "desc"):
        """
        List bookings with role-based filtering:
        - ADMIN, MANAGER: see all bookings
        - REGULAR: see only own bookings (created_by == user.id)
        """
        query = db.query(models.Booking).options(joinedload(models.Booking.guest))
        
        # Filter by role
        if current_user and current_user.permission_level == models.PermissionLevel.REGULAR:
            query = query.filter(models.Booking.created_by == current_user.id)
        
        # Apply filters
        if status:
            query = query.filter(models.Booking.status == status)
        if check_in_from:
            query = query.filter(models.Booking.check_in >= check_in_from)
        if check_in_to:
            query = query.filter(models.Booking.check_in <= check_in_to)
        
        # Apply sorting (default to created_at desc)
        if not sort_by:
            sort_by = "created_at"
        query = apply_sorting(query, models.Booking, sort_by, sort_order)
        
        # Apply pagination
        return paginate(query, page, page_size)

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
        
        # Calculate final bill based on actual nights; fallback to original booking nights
        if booking.actual_check_in:
            actual_nights = (booking.actual_check_out - booking.actual_check_in).days
            if actual_nights <= 0:
                # If actual timestamps are on the same day (tests or quick check-outs),
                # fall back to the originally booked nights to avoid a zero final bill.
                actual_nights = (booking.check_out - booking.check_in).days
            booking.final_bill = actual_nights * booking.price_per_night
        
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def cancel_booking(db: Session, booking_id: int):
        """Transition from PENDING/CONFIRMED to CANCELLED and auto-process refunds."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.CANCELLED)
        
        booking.status = models.BookingStatus.CANCELLED.value
        booking.cancelled_at = datetime.now()
        db.commit()
        db.refresh(booking)
        
        # Auto-process refunds based on cancellation policy
        RefundPolicyService.process_cancellation_refunds(db, booking)
        
        return booking

    @staticmethod
    def mark_no_show(db: Session, booking_id: int):
        """Transition from CONFIRMED to NO_SHOW and charge no-show fee (full bill)."""
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        
        current_status = models.BookingStatus(booking.status)
        BookingService._validate_transition(current_status, models.BookingStatus.NO_SHOW)
        
        booking.status = models.BookingStatus.NO_SHOW.value
        db.commit()
        db.refresh(booking)
        
        # Auto-charge full final bill for no-show
        # Set final_bill if not already set (use total_price as fallback)
        final_bill = booking.final_bill or booking.total_price
        
        if final_bill and final_bill > 0:
            no_show_charge = models.Payment(
                booking_id=booking.id,
                amount=final_bill,
                currency="USD",
                method="no_show_charge",
                status=models.Payment.PaymentStatus.PAID.value,
                processed_at=datetime.now(),
                reference=f"No-show charge for booking {booking.booking_number}",
            )
            db.add(no_show_charge)
            db.commit()
        
        return booking
