from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..core.security import get_current_user
from ..dependencies.security import require_role
from ..db import models
from ..schemas.payment import PaymentCreate, PaymentResponse
from ..services.payment_service import PaymentService
from ..utils.pagination import PaginatedResponse
from ..utils.audit import log_payment_action

router = APIRouter(prefix="/payments")

@router.get("/", response_model=PaginatedResponse[PaymentResponse])
def list_payments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        payments = PaymentService.list_payments(db, current_user, page, page_size, status, sort_by, sort_order)
        return payments
    except HTTPException as e:
        raise e

@router.post("/create", response_model=PaymentResponse)
def create_payment(
    payment_in: PaymentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        payment = PaymentService.create_payment(db, payment_in.booking_id, payment_in.amount, payment_in.method, payment_in.currency)
        
        # Log audit
        log_payment_action(
            db=db,
            user=current_user,
            action="CREATE",
            payment_id=payment.id,
            description=f"Created payment for booking ID {payment.booking_id}, amount {payment.amount} {payment.currency}",
            new_values={
                "booking_id": payment.booking_id,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "method": payment.method,
                "status": payment.status.value
            },
            request=request
        )
        
        return payment
    except HTTPException as e:
        raise e

@router.post("/{payment_id}/process", response_model=PaymentResponse)
def process_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        payment = PaymentService.process_payment(db, payment_id)
        
        # Log audit
        log_payment_action(
            db=db,
            user=current_user,
            action="PROCESS",
            payment_id=payment.id,
            description=f"Processed payment ID {payment.id} for {payment.amount} {payment.currency}",
            old_values={"status": "PENDING"},
            new_values={"status": payment.status.value},
            request=request
        )
        
        return payment
    except HTTPException as e:
        raise e

@router.post("/{payment_id}/fail", response_model=PaymentResponse)
def fail_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))):
    try:
        payment = PaymentService.fail_payment(db, payment_id)
        return payment
    except HTTPException as e:
        raise e

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))
):
    try:
        payment = PaymentService.refund_payment(db, payment_id)
        
        # Log audit
        log_payment_action(
            db=db,
            user=current_user,
            action="REFUND",
            payment_id=payment.id,
            description=f"Refunded payment ID {payment.id} for {payment.amount} {payment.currency}",
            old_values={"status": "PAID"},
            new_values={"status": payment.status.value},
            request=request
        )
        
        return payment
    except HTTPException as e:
        raise e
