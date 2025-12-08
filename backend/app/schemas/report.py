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
    daily: List[OccupancyDay]


class RevenueDay(BaseModel):
    date: date
    revenue: Decimal


class RevenueReport(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal
    daily: List[RevenueDay]


class TrendsReport(BaseModel):
    start_date: date
    end_date: date
    total_bookings: int
    cancellations: int
    no_shows: int
    cancellation_rate: Decimal  # percent
    no_show_rate: Decimal  # percent
