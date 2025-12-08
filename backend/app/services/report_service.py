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
        # Total rooms count
        total_rooms = db.query(func.count(models.Room.id)).scalar() or 0
        total_rooms = int(total_rooms)

        # Build occupancy map for all dates in bulk
        # Get all bookings that overlap with our date range
        bookings = db.query(models.Booking).filter(
            models.Booking.check_in < (end_date + timedelta(days=1)),
            models.Booking.check_out > start_date,
            models.Booking.status.in_([
                models.BookingStatus.CONFIRMED.value,
                models.BookingStatus.CHECKED_IN.value,
                models.BookingStatus.CHECKED_OUT.value,  # Include checked out bookings
            ])
        ).all()

        # Count occupied rooms per day
        occupancy_by_date = {}
        for d in _daterange(start_date, end_date):
            count = sum(1 for b in bookings if b.check_in <= d < b.check_out)
            occupancy_by_date[d] = count

        # Build daily array and calculate metrics
        daily = []
        total_occupied = 0
        total_room_nights = 0
        occupancy_rates = []
        
        for d in _daterange(start_date, end_date):
            occupied = occupancy_by_date.get(d, 0)
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
            total_room_nights += occupied
            occupancy_rates.append(occupancy_rate)

        days = len(daily)
        avg = Decimal('0')
        if days > 0 and total_rooms > 0:
            avg = (Decimal(total_occupied) / Decimal(days * total_rooms) * Decimal('100')).quantize(Decimal('0.01'))

        max_occupancy = max(occupancy_rates, default=Decimal('0'))
        min_occupancy = min(occupancy_rates, default=Decimal('0'))

        return {
            'start_date': start_date,
            'end_date': end_date,
            'average_occupancy': avg,
            'max_occupancy': max_occupancy,
            'min_occupancy': min_occupancy,
            'total_room_nights': total_room_nights,
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

        # Calculate metrics
        num_days = len(daily)
        avg_daily = Decimal('0')
        if num_days > 0:
            avg_daily = (total / Decimal(num_days)).quantize(Decimal('0.01'))
        
        max_daily = max((d['revenue'] for d in daily), default=Decimal('0'))
        min_daily = min((d['revenue'] for d in daily), default=Decimal('0'))
        
        # Count UNIQUE paid bookings (not payment records) in date range
        paid_bookings_count = db.query(func.count(func.distinct(models.Payment.booking_id))).filter(
            models.Payment.status == models.Payment.PaymentStatus.PAID.value,
            models.Payment.processed_at != None,
            func.date(models.Payment.processed_at) >= start_date,
            func.date(models.Payment.processed_at) <= end_date
        ).scalar() or 0

        # Revenue breakdown by room type
        revenue_by_room_type = db.query(
            models.RoomType.name,
            func.coalesce(func.sum(models.Payment.amount), 0).label('revenue')
        ).join(models.Booking, models.Payment.booking_id == models.Booking.id)\
         .join(models.Room, models.Booking.room_id == models.Room.id)\
         .join(models.RoomType, models.Room.room_type_id == models.RoomType.id)\
         .filter(
            models.Payment.status == models.Payment.PaymentStatus.PAID.value,
            models.Payment.processed_at != None,
            func.date(models.Payment.processed_at) >= start_date,
            func.date(models.Payment.processed_at) <= end_date
        ).group_by(models.RoomType.name).all()

        room_type_breakdown = [
            {'room_type': name, 'revenue': Decimal(rev).quantize(Decimal('0.01'))}
            for name, rev in revenue_by_room_type
        ]

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total.quantize(Decimal('0.01')),
            'average_daily_revenue': avg_daily,
            'max_daily_revenue': max_daily.quantize(Decimal('0.01')),
            'min_daily_revenue': min_daily.quantize(Decimal('0.01')),
            'total_paid_bookings': int(paid_bookings_count),
            'room_type_breakdown': room_type_breakdown,
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

        # Count by status
        confirmed_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.status.in_([
                models.BookingStatus.CONFIRMED.value,
                models.BookingStatus.CHECKED_IN.value,
                models.BookingStatus.CHECKED_OUT.value,
            ]),
            models.Booking.created_at >= start_date,
            models.Booking.created_at < (end_date + timedelta(days=1)),
        )
        confirmed = int(confirmed_q.scalar() or 0)

        cancellations_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.status == models.BookingStatus.CANCELLED.value,
            models.Booking.cancelled_at >= start_date,
            models.Booking.cancelled_at < (end_date + timedelta(days=1)),
        )
        cancellations = int(cancellations_q.scalar() or 0)

        no_shows_q = db.query(func.count(models.Booking.id)).filter(
            models.Booking.status == models.BookingStatus.NO_SHOW.value,
            models.Booking.created_at >= start_date,
            models.Booking.created_at < (end_date + timedelta(days=1)),
        )
        no_shows = int(no_shows_q.scalar() or 0)

        # Calculate average booking lead time (days between created_at and check_in)
        # Get all bookings and calculate in Python for cross-database compatibility
        bookings_for_stats = db.query(
            models.Booking.created_at,
            models.Booking.check_in,
            models.Booking.check_out
        ).filter(
            models.Booking.created_at >= start_date,
            models.Booking.created_at < (end_date + timedelta(days=1)),
        ).all()

        total_lead_time = 0
        total_stay_length = 0
        count = len(bookings_for_stats)
        
        for booking in bookings_for_stats:
            # Lead time: days from creation to check-in
            lead_days = (booking.check_in - booking.created_at.date()).days
            total_lead_time += lead_days
            
            # Length of stay: nights
            stay_nights = (booking.check_out - booking.check_in).days
            total_stay_length += stay_nights
        
        avg_lead_time = Decimal(total_lead_time / count).quantize(Decimal('0.01')) if count > 0 else Decimal('0')
        avg_length_of_stay = Decimal(total_stay_length / count).quantize(Decimal('0.01')) if count > 0 else Decimal('0')

        # Daily breakdown for temporal chart
        daily_bookings = db.query(
            func.date(models.Booking.created_at).label('day'),
            func.count(models.Booking.id).label('count')
        ).filter(
            models.Booking.created_at >= start_date,
            models.Booking.created_at < (end_date + timedelta(days=1)),
        ).group_by('day').all()

        daily_map = {}
        for row in daily_bookings:
            day_val = row.day
            if isinstance(day_val, str):
                try:
                    day_obj = date.fromisoformat(day_val)
                except Exception:
                    day_obj = day_val
            else:
                day_obj = day_val
            daily_map[day_obj] = int(row.count)

        daily = []
        for d in _daterange(start_date, end_date):
            daily.append({'date': d, 'bookings': daily_map.get(d, 0)})

        # Calculate rates
        cancellation_rate = Decimal('0')
        no_show_rate = Decimal('0')
        if total > 0:
            cancellation_rate = (Decimal(cancellations) / Decimal(total) * Decimal('100')).quantize(Decimal('0.01'))
            no_show_rate = (Decimal(no_shows) / Decimal(total) * Decimal('100')).quantize(Decimal('0.01'))

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_bookings': total,
            'confirmed_bookings': confirmed,
            'cancellations': cancellations,
            'no_shows': no_shows,
            'cancellation_rate': cancellation_rate,
            'no_show_rate': no_show_rate,
            'avg_lead_time_days': avg_lead_time,
            'avg_length_of_stay_nights': avg_length_of_stay,
            'daily': daily,
        }
