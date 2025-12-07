import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db import models
from backend.app.utils.availability import is_room_available


@pytest.fixture()
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    yield Session()
    Session().close()


def make_booking(session, room_id, check_in, check_out, status="confirmed", booking_number=None):
    # Ensure room exists
    room = session.query(models.Room).filter_by(id=room_id).first()
    if not room:
        rt = models.RoomType(name=f"RT-{room_id}", base_price=100, capacity=2)
        session.add(rt)
        session.commit()
        room = models.Room(number=str(room_id), room_type_id=rt.id, price_per_night=100)
        session.add(room)
        session.commit()

    booking = models.Booking(
        booking_number=booking_number or f"BK-{room_id}-{check_in}",
        guest_id=1,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        number_of_guests=1,
        price_per_night=100,
        total_price=100 * (check_out - check_in).days,
        status=status,
    )
    session.add(booking)
    session.commit()
    return booking


def test_room_available_when_no_bookings(in_memory_db):
    session = in_memory_db
    # Create a room
    rt = models.RoomType(name="Single", base_price=50, capacity=1)
    session.add(rt)
    session.commit()
    room = models.Room(number="101", room_type_id=rt.id, price_per_night=50)
    session.add(room)
    session.commit()

    assert is_room_available(session, room.id, date(2025, 12, 10), date(2025, 12, 12)) is True


def test_room_not_available_when_overlapping_booking(in_memory_db):
    session = in_memory_db
    # add booking
    booking = make_booking(session, room_id=1, check_in=date(2025, 12, 10), check_out=date(2025, 12, 15))

    # overlapping range
    assert is_room_available(session, booking.room_id, date(2025, 12, 12), date(2025, 12, 14)) is False


def test_room_available_with_excluded_booking_id(in_memory_db):
    session = in_memory_db
    booking = make_booking(session, room_id=1, check_in=date(2025, 12, 10), check_out=date(2025, 12, 15))

    # If we exclude the booking id (e.g., updating the same booking), it should be allowed
    assert is_room_available(session, booking.room_id, date(2025, 12, 12), date(2025, 12, 14), exclude_booking_id=booking.id) is True


def test_room_available_when_other_room_booked(in_memory_db):
    session = in_memory_db
    # booking in room 1
    make_booking(session, room_id=1, check_in=date(2025, 12, 10), check_out=date(2025, 12, 15))
    # Ensure room 2 exists
    rt2 = models.RoomType(name="Double", base_price=80, capacity=2)
    session.add(rt2)
    session.commit()
    room2 = models.Room(number="102", room_type_id=rt2.id, price_per_night=80)
    session.add(room2)
    session.commit()

    assert is_room_available(session, room2.id, date(2025, 12, 12), date(2025, 12, 14)) is True
