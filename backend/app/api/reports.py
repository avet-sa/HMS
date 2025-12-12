from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from ..db.session import get_db
from ..dependencies.security import require_role
from ..db import models
from ..services.report_service import ReportService
from ..services.housekeeping_report_service import HousekeepingReportService
from ..schemas.report import OccupancyReport, RevenueReport, TrendsReport
from ..schemas.housekeeping_report import (
    HousekeepingDashboard,
    StaffPerformanceReport,
    RoomStatusGrid
)

router = APIRouter()


@router.get("/occupancy", response_model=OccupancyReport)
def occupancy_report(start_date: date, end_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")
    data = ReportService.occupancy_report(db, start_date, end_date)
    return data


@router.get("/revenue", response_model=RevenueReport)
def revenue_report(start_date: date, end_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")
    data = ReportService.revenue_report(db, start_date, end_date)
    return data


@router.get("/trends", response_model=TrendsReport)
def booking_trends(start_date: date, end_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")
    data = ReportService.booking_trends(db, start_date, end_date)
    return data


# Housekeeping Reports
@router.get("/housekeeping/dashboard", response_model=HousekeepingDashboard)
def housekeeping_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.REGULAR, models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))
):
    """Get housekeeping dashboard with task statistics and room status"""
    data = HousekeepingReportService.get_dashboard(db)
    return data


@router.get("/housekeeping/staff-performance", response_model=StaffPerformanceReport)
def staff_performance(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))
):
    """Get staff performance metrics for a date range"""
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be <= end_date")
    data = HousekeepingReportService.get_staff_performance(db, start_date, end_date)
    return data


@router.get("/housekeeping/room-status-grid", response_model=RoomStatusGrid)
def room_status_grid(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.REGULAR, models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))
):
    """Get grid view of all rooms with their housekeeping status"""
    data = HousekeepingReportService.get_room_status_grid(db)
    return data
