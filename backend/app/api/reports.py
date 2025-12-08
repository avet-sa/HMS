from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from ..db.session import get_db
from ..dependencies.security import require_role
from ..db import models
from ..services.report_service import ReportService
from ..schemas.report import OccupancyReport, RevenueReport, TrendsReport

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
