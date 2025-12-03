from sqlalchemy.orm import Session
from datetime import datetime

from app.db import models
from app.schemas.booking import BookingCreate, BookingUpdate
from app.utils.availability import is_room_available


class BookingService:

    @staticmethod
    def create_booking(db: Session, data: BookingCreate) -> models.Booking:
        # Check room availability
        if not is_room_available(db, data.room_id, data.check_in, data.check_out):
            raise ValueError("Room is not available for the selected dates.")

        booking = models.Booking(
            room_id=data.room_id,
            guest_id=data.guest_id,
            check_in=data.check_in,
            check_out=data.check_out,
            status="booked",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_booking(db: Session, booking_id: int) -> models.Booking | None:
        return db.query(models.Booking).filter(models.Booking.id == booking_id).first()

    @staticmethod
    def list_bookings(db: Session):
        return db.query(models.Booking).all()

    @staticmethod
    def update_booking(db: Session, booking_id: int, data: BookingUpdate):
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            return None

        # If room or dates changed → check availability
        if (data.room_id and data.room_id != booking.room_id) or \
           (data.check_in or data.check_out):
            if not is_room_available(
                db,
                data.room_id or booking.room_id,
                data.check_in or booking.check_in,
                data.check_out or booking.check_out,
                exclude_booking_id=booking_id
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
