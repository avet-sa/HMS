from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import List


class OccupancyDay(BaseModel):
    date: date
    occupied: int
    total_rooms: int
    occupancy_rate: Decimal  # percentage 0-100


class OccupancyReport(BaseModel):
    start_date: date
    end_date: date
    average_occupancy: Decimal
    max_occupancy: Decimal
    min_occupancy: Decimal
    total_room_nights: int
    daily: List[OccupancyDay]


class RevenueDay(BaseModel):
    date: date
    revenue: Decimal


class RoomTypeRevenue(BaseModel):
    room_type: str
    revenue: Decimal


class RevenueReport(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal
    average_daily_revenue: Decimal
    max_daily_revenue: Decimal
    min_daily_revenue: Decimal
    total_paid_bookings: int
    room_type_breakdown: List[RoomTypeRevenue]
    daily: List[RevenueDay]


class TrendsDay(BaseModel):
    date: date
    bookings: int


class TrendsReport(BaseModel):
    start_date: date
    end_date: date
    total_bookings: int
    confirmed_bookings: int
    cancellations: int
    no_shows: int
    cancellation_rate: Decimal  # percent
    no_show_rate: Decimal  # percent
    avg_lead_time_days: Decimal
    avg_length_of_stay_nights: Decimal
    daily: List[TrendsDay]
