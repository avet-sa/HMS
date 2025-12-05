from uuid import uuid4

from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from ..db import models
from ..utils.availability import is_room_available
from ..schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    # noinspection PyTypeChecker
    @staticmethod
    def create_booking(db: Session, data: BookingCreate) -> models.Booking:
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
            check_in=data.check_in,
            check_out=data.check_out,
            number_of_guests=data.number_of_guests,
            price_per_night=price_per_night,
            total_price=total_price,
            status=data.status or "pending",
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
    def list_bookings(db: Session):
        return (
            db.query(models.Booking)
            .options(joinedload(models.Booking.guest))
            .all()
        )

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
    def cancel_booking(db: Session, booking_id: int):
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        booking.status = "cancelled"
        db.commit()
        return booking

    @staticmethod
    def check_in(db: Session, booking_id: int):
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        booking.status = "checked_in"
        booking.actual_check_in = datetime.now()
        db.commit()
        return booking

    @staticmethod
    def check_out(db: Session, booking_id: int):
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None
        booking.status = "checked_out"
        booking.actual_check_out = datetime.now()

        # Free room
        room = db.query(models.Room).filter(models.Room.id == booking.room_id).first()
        if room:
            room.is_available = True

        db.commit()
        return booking
