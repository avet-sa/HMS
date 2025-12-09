"""
Audit logging utility for tracking all critical operations
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Request

from ...app.db.models import AuditLog, User


def log_audit(
    db: Session,
    user: Optional[User],
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    description: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """
    Create an audit log entry
    
    Args:
        db: Database session
        user: User who performed the action (can be None for system actions)
        action: Action performed (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.)
        entity_type: Type of entity affected (booking, payment, room, user, etc.)
        entity_id: ID of the affected entity
        description: Human-readable description of the action
        old_values: Dictionary of old values (for UPDATE/DELETE)
        new_values: Dictionary of new values (for CREATE/UPDATE)
        request: FastAPI Request object (for extracting IP and user agent)
    
    Returns:
        Created AuditLog instance
    """
    # Get IP address
    ip_address = None
    user_agent = None
    if request:
        # Try to get real IP from X-Forwarded-For header (for proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.client.host if request.client else None
        
        # Get user agent
        user_agent = request.headers.get("User-Agent")
    
    # Convert values to JSON strings
    old_values_json = json.dumps(old_values) if old_values else None
    new_values_json = json.dumps(new_values) if new_values else None
    
    # Truncate if too long (max 2000 chars)
    if old_values_json and len(old_values_json) > 2000:
        old_values_json = old_values_json[:1997] + "..."
    if new_values_json and len(new_values_json) > 2000:
        new_values_json = new_values_json[:1997] + "..."
    
    # Create audit log entry
    audit_log = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "SYSTEM",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_values=old_values_json,
        new_values=new_values_json,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


def log_login(db: Session, user: User, request: Request, success: bool = True):
    """Log user login attempt"""
    action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    description = f"User {user.username} logged in successfully" if success else f"Failed login attempt for {user.username}"
    
    return log_audit(
        db=db,
        user=user if success else None,
        action=action,
        entity_type="user",
        entity_id=user.id,
        description=description,
        request=request
    )


def log_logout(db: Session, user: User, request: Request):
    """Log user logout"""
    return log_audit(
        db=db,
        user=user,
        action="LOGOUT",
        entity_type="user",
        entity_id=user.id,
        description=f"User {user.username} logged out",
        request=request
    )


def log_booking_action(
    db: Session,
    user: User,
    action: str,
    booking_id: int,
    description: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Log booking-related actions"""
    return log_audit(
        db=db,
        user=user,
        action=action,
        entity_type="booking",
        entity_id=booking_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        request=request
    )


def log_payment_action(
    db: Session,
    user: User,
    action: str,
    payment_id: int,
    description: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
):
    """Log payment-related actions"""
    return log_audit(
        db=db,
        user=user,
        action=action,
        entity_type="payment",
        entity_id=payment_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        request=request
    )
