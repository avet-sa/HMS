from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from typing import List, Dict
from ..db import models


class HousekeepingReportService:
    """Service for housekeeping reporting and analytics"""
    
    @staticmethod
    def get_dashboard(db: Session) -> Dict:
        """Get housekeeping dashboard statistics"""
        
        # Task counts by status
        total_tasks = db.query(func.count(models.HousekeepingTask.id)).scalar() or 0
        
        status_counts = db.query(
            models.HousekeepingTask.status,
            func.count(models.HousekeepingTask.id)
        ).group_by(models.HousekeepingTask.status).all()
        
        status_map = {status: count for status, count in status_counts}
        pending_tasks = status_map.get(models.TaskStatus.PENDING.value, 0)
        in_progress_tasks = status_map.get(models.TaskStatus.IN_PROGRESS.value, 0)
        completed_tasks = status_map.get(models.TaskStatus.COMPLETED.value, 0)
        verified_tasks = status_map.get(models.TaskStatus.VERIFIED.value, 0)
        
        # Task counts by priority
        priority_counts = db.query(
            models.HousekeepingTask.priority,
            func.count(models.HousekeepingTask.id)
        ).group_by(models.HousekeepingTask.priority).all()
        
        priority_map = {priority: count for priority, count in priority_counts}
        urgent_tasks = priority_map.get(models.TaskPriority.URGENT.value, 0)
        high_priority_tasks = priority_map.get(models.TaskPriority.HIGH.value, 0)
        normal_priority_tasks = priority_map.get(models.TaskPriority.NORMAL.value, 0)
        low_priority_tasks = priority_map.get(models.TaskPriority.LOW.value, 0)
        
        # Today's metrics
        today = date.today()
        tasks_scheduled_today = db.query(func.count(models.HousekeepingTask.id)).filter(
            models.HousekeepingTask.scheduled_date == today
        ).scalar() or 0
        
        tasks_completed_today = db.query(func.count(models.HousekeepingTask.id)).filter(
            func.date(models.HousekeepingTask.completed_at) == today
        ).scalar() or 0
        
        checkout_cleanings_pending = db.query(func.count(models.HousekeepingTask.id)).filter(
            models.HousekeepingTask.is_checkout_cleaning == True,
            models.HousekeepingTask.status.in_([
                models.TaskStatus.PENDING.value,
                models.TaskStatus.IN_PROGRESS.value
            ])
        ).scalar() or 0
        
        # Room status summary
        room_status_counts = db.query(
            models.Room.maintenance_status,
            func.count(models.Room.id)
        ).group_by(models.Room.maintenance_status).all()
        
        room_status_map = {status: count for status, count in room_status_counts}
        rooms_available = room_status_map.get(models.RoomMaintenanceStatus.AVAILABLE, 0)
        rooms_in_maintenance = room_status_map.get(models.RoomMaintenanceStatus.MAINTENANCE, 0)
        rooms_out_of_service = room_status_map.get(models.RoomMaintenanceStatus.OUT_OF_SERVICE, 0)
        
        # Build response lists
        tasks_by_status = [
            {"status": status, "count": count}
            for status, count in status_counts
        ]
        
        tasks_by_priority = [
            {"priority": priority, "count": count}
            for priority, count in priority_counts
        ]
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "verified_tasks": verified_tasks,
            "urgent_tasks": urgent_tasks,
            "high_priority_tasks": high_priority_tasks,
            "normal_priority_tasks": normal_priority_tasks,
            "low_priority_tasks": low_priority_tasks,
            "tasks_scheduled_today": tasks_scheduled_today,
            "tasks_completed_today": tasks_completed_today,
            "checkout_cleanings_pending": checkout_cleanings_pending,
            "rooms_available": rooms_available,
            "rooms_in_maintenance": rooms_in_maintenance,
            "rooms_out_of_service": rooms_out_of_service,
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
        }
    
    @staticmethod
    def get_staff_performance(db: Session, start_date: date, end_date: date) -> Dict:
        """Get staff performance metrics for a date range"""
        
        # Get all staff who completed or verified tasks in the date range
        staff_ids = set()
        
        # Get staff who completed tasks
        completed_tasks = db.query(models.HousekeepingTask).filter(
            models.HousekeepingTask.completed_at.isnot(None),
            func.date(models.HousekeepingTask.completed_at) >= start_date,
            func.date(models.HousekeepingTask.completed_at) <= end_date
        ).all()
        
        for task in completed_tasks:
            if task.assigned_to:
                staff_ids.add(task.assigned_to)
        
        # Get staff who verified tasks
        verified_tasks = db.query(models.HousekeepingTask).filter(
            models.HousekeepingTask.verified_at.isnot(None),
            func.date(models.HousekeepingTask.verified_at) >= start_date,
            func.date(models.HousekeepingTask.verified_at) <= end_date
        ).all()
        
        for task in verified_tasks:
            if task.verified_by:
                staff_ids.add(task.verified_by)
        
        # Build metrics for each staff member
        staff_metrics = []
        total_tasks_completed = 0
        total_tasks_verified = 0
        total_duration_minutes = 0
        total_duration_count = 0
        
        for staff_id in staff_ids:
            user = db.query(models.User).filter(models.User.id == staff_id).first()
            if not user:
                continue
            
            # Tasks completed by this staff
            completed = db.query(models.HousekeepingTask).filter(
                models.HousekeepingTask.assigned_to == staff_id,
                models.HousekeepingTask.completed_at.isnot(None),
                func.date(models.HousekeepingTask.completed_at) >= start_date,
                func.date(models.HousekeepingTask.completed_at) <= end_date
            ).all()
            
            # Tasks verified by this staff
            verified = db.query(models.HousekeepingTask).filter(
                models.HousekeepingTask.verified_by == staff_id,
                models.HousekeepingTask.verified_at.isnot(None),
                func.date(models.HousekeepingTask.verified_at) >= start_date,
                func.date(models.HousekeepingTask.verified_at) <= end_date
            ).count()
            
            # Calculate average duration and total hours
            durations = [task.actual_duration_minutes for task in completed if task.actual_duration_minutes]
            avg_duration = Decimal(sum(durations) / len(durations)) if durations else Decimal('0')
            total_minutes = sum(durations) if durations else 0
            total_hours = Decimal(total_minutes) / Decimal('60')
            
            staff_metrics.append({
                "user_id": staff_id,
                "username": user.username,
                "tasks_completed": len(completed),
                "tasks_verified": verified,
                "average_duration_minutes": avg_duration.quantize(Decimal('0.01')),
                "total_hours_worked": total_hours.quantize(Decimal('0.01'))
            })
            
            total_tasks_completed += len(completed)
            total_tasks_verified += verified
            if durations:
                total_duration_minutes += sum(durations)
                total_duration_count += len(durations)
        
        # Calculate overall average completion time
        average_completion_time = Decimal('0')
        if total_duration_count > 0:
            average_completion_time = (Decimal(total_duration_minutes) / Decimal(total_duration_count)).quantize(Decimal('0.01'))
        
        # Sort by tasks completed descending
        staff_metrics.sort(key=lambda x: x["tasks_completed"], reverse=True)
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "staff_metrics": staff_metrics,
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_verified": total_tasks_verified,
            "average_completion_time_minutes": average_completion_time
        }
    
    @staticmethod
    def get_room_status_grid(db: Session) -> Dict:
        """Get grid view of all rooms with housekeeping status"""
        
        today = date.today()
        
        # Get all rooms with their room type
        rooms = db.query(models.Room).join(models.RoomType).all()
        
        room_info_list = []
        status_summary = {}
        
        for room in rooms:
            # Check for pending/in-progress tasks
            pending_tasks = db.query(models.HousekeepingTask).filter(
                models.HousekeepingTask.room_id == room.id,
                models.HousekeepingTask.status == models.TaskStatus.PENDING.value
            ).count()
            
            in_progress_tasks = db.query(models.HousekeepingTask).filter(
                models.HousekeepingTask.room_id == room.id,
                models.HousekeepingTask.status == models.TaskStatus.IN_PROGRESS.value
            ).count()
            
            # Find next booking check-in
            next_booking = db.query(models.Booking).filter(
                models.Booking.room_id == room.id,
                models.Booking.check_in >= today,
                models.Booking.status.in_([
                    models.BookingStatus.CONFIRMED.value,
                    models.BookingStatus.PENDING.value
                ])
            ).order_by(models.Booking.check_in).first()
            
            next_checkin = next_booking.check_in if next_booking else None
            
            # Get maintenance status as string
            maintenance_status = room.maintenance_status.value if hasattr(room.maintenance_status, 'value') else str(room.maintenance_status)
            
            room_info_list.append({
                "room_id": room.id,
                "room_number": room.number,
                "room_type": room.room_type.name,
                "maintenance_status": maintenance_status,
                "has_pending_tasks": pending_tasks > 0,
                "has_in_progress_tasks": in_progress_tasks > 0,
                "next_booking_checkin": next_checkin
            })
            
            # Update summary
            status_summary[maintenance_status] = status_summary.get(maintenance_status, 0) + 1
        
        # Sort by room number
        room_info_list.sort(key=lambda x: x["room_number"])
        
        return {
            "as_of_date": today,
            "rooms": room_info_list,
            "summary": status_summary
        }
