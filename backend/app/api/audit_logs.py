"""
API endpoints for audit logs
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..db.models import AuditLog, User
from ..schemas.audit_log import AuditLogResponse
from ..utils.pagination import paginate, apply_sorting, PaginatedResponse
from ..dependencies.security import get_current_user
from ..core.permissions import require_admin_or_manager

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=PaginatedResponse[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order")
):
    """
    List all audit logs with filtering and pagination
    Requires: ADMIN or MANAGER role
    """
    # Check permission
    require_admin_or_manager(current_user)
    
    # Build query
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action.upper())
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type.lower())
    
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    
    if date_from:
        query = query.filter(AuditLog.created_at >= date_from)
    
    if date_to:
        query = query.filter(AuditLog.created_at <= date_to)
    
    # Apply sorting
    query = apply_sorting(query, AuditLog, sort_by, sort_order)
    
    # Paginate
    return paginate(query, page, page_size)


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific audit log by ID
    Requires: ADMIN or MANAGER role
    """
    # Check permission
    require_admin_or_manager(current_user)
    
    # Get audit log
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    return audit_log
