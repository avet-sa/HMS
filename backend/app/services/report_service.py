from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..db import models


def _daterange(start_date: date, end_date: date):
    cur = start_date
    while cur <= end_date:
        yield cur
        cur = cur + timedelta(days=1)


class ReportService:
    @staticmethod
    def occupancy_report(db: Session, start_date: date, end_date: date):
        # total rooms
        total_rooms = db.query(func.count(models.Room.id)).scalar() or 0
        total_rooms = int(total_rooms)

        daily = []
        total_occupied = 0
        days = 0
        for d in _daterange(start_date, end_date):
            occupied_q = db.query(func.count(models.Booking.id)).filter(
                models.Booking.check_in <= d,
                models.Booking.check_out > d,
                models.Booking.status.in_([
                    models.BookingStatus.CONFIRMED.value,
                    models.BookingStatus.CHECKED_IN.value,
                ])
            )
            occupied = occupied_q.scalar() or 0
            occupied = int(occupied)
            occupancy_rate = Decimal('0')
            if total_rooms > 0:
                occupancy_rate = (Decimal(occupied) / Decimal(total_rooms) * Decimal('100')).quantize(Decimal('0.01'))
            daily.append({
                'date': d,
                'occupied': occupied,
                'total_rooms': total_rooms,
                'occupancy_rate': occupancy_rate,
            })
            total_occupied += occupied
            days += 1

        avg = Decimal('0')
        if days > 0 and total_rooms > 0:
            avg = (Decimal(total_occupied) / Decimal(days * total_rooms) * Decimal('100')).quantize(Decimal('0.01'))

        return {
            'start_date': start_date,
            'end_date': end_date,
            'average_occupancy': avg,
            'daily': daily,
        }

    @staticmethod
    def revenue_report(db: Session, start_date: date, end_date: date):
        # Sum PAID payments by date(processed_at)
        # Use date(trunc) via func.date
        # Use func.date to normalize datetime->date for grouping and filtering so it works
        # across SQLite/Postgres. Exclude null processed_at values.
        q = db.query(
            func.date(models.Payment.processed_at).label('day'),
            func.coalesce(func.sum(models.Payment.amount), 0).label('revenue')
        ).filter(
            models.Payment.status == models.Payment.PaymentStatus.PAID.value,
            models.Payment.processed_at != None,
        )
        q = q.filter(func.date(models.Payment.processed_at) >= start_date, func.date(models.Payment.processed_at) <= end_date)
        q = q.group_by('day')

        rows = {}
        for r in q.all():
            day_val = r.day
            # SQLite returns string for func.date, Postgres returns date
            if isinstance(day_val, str):
                try:
                    day_obj = date.fromisoformat(day_val)
                except Exception:
                    day_obj = day_val
            else:
                day_obj = day_val
            rows[day_obj] = Decimal(r.revenue)

        daily = []
        total = Decimal('0')
        for d in _daterange(start_date, end_date):
            rev = rows.get(d) or Decimal('0')
            rev = Decimal(rev).quantize(Decimal('0.01'))
            daily.append({'date': d, 'revenue': rev})
            total += rev

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total.quantize(Decimal('0.01')),
            'daily': daily,
        }

    @staticmethod
    def booking_trends(db: Session, start_date: date, end_date: date):
        # Count bookings created in window
        total_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.created_at >= start_date,
            models.Booking.created_at < (end_date + timedelta(days=1)),
        )
        total = total_q.scalar() or 0
        total = int(total)

        cancellations_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.status == models.BookingStatus.CANCELLED.value,
            models.Booking.cancelled_at >= start_date,
            models.Booking.cancelled_at < (end_date + timedelta(days=1)),
        )
        cancellations = int(cancellations_q.scalar() or 0)

        no_shows_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.status == models.BookingStatus.NO_SHOW.value,
            models.Booking.updated_at >= start_date,  # fallback if no specific timestamp
            models.Booking.updated_at < (end_date + timedelta(days=1)),
        )
        no_shows = int(no_shows_q.scalar() or 0)

        cancellation_rate = Decimal('0')
        no_show_rate = Decimal('0')
        if total > 0:
            cancellation_rate = (Decimal(cancellations) / Decimal(total) * Decimal('100')).quantize(Decimal('0.01'))
            no_show_rate = (Decimal(no_shows) / Decimal(total) * Decimal('100')).quantize(Decimal('0.01'))

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_bookings': total,
            'cancellations': cancellations,
            'no_shows': no_shows,
            'cancellation_rate': cancellation_rate,
            'no_show_rate': no_show_rate,
        }
