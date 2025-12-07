from typing import Optional
from datetime import date
from ..db import models


def is_room_available(db, room_id: int, check_in: date, check_out: date, exclude_booking_id: Optional[int] = None) -> bool:
	"""Return True if no active booking overlaps the given date range for the room.
	
	Only CONFIRMED and CHECKED_IN bookings block availability.
	Ignores CANCELLED, NO_SHOW, and CHECKED_OUT bookings.
	"""
	query = db.query(models.Booking).filter(
		models.Booking.room_id == room_id,
		models.Booking.check_out > check_in,
		models.Booking.check_in < check_out,
		models.Booking.status.in_([
			models.BookingStatus.CONFIRMED.value,
			models.BookingStatus.CHECKED_IN.value,
		])
	)
	if exclude_booking_id:
		query = query.filter(models.Booking.id != exclude_booking_id)
	return query.first() is None
