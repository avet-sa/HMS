from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..core.security import get_current_user
from ..dependencies.security import require_role
from ..db import models
from ..schemas.payment import PaymentCreate, PaymentResponse
from ..services.payment_service import PaymentService

router = APIRouter(prefix="/payments")

@router.get("/", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        payments = PaymentService.list_payments(db, current_user)
        return payments
    except HTTPException as e:
        raise e

@router.post("/create", response_model=PaymentResponse)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        payment = PaymentService.create_payment(db, payment_in.booking_id, payment_in.amount, payment_in.method, payment_in.currency)
        return payment
    except HTTPException as e:
        raise e

@router.post("/{payment_id}/process", response_model=PaymentResponse)
def process_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))):
    try:
        payment = PaymentService.process_payment(db, payment_id)
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
def refund_payment(payment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))):
    try:
        payment = PaymentService.refund_payment(db, payment_id)
        return payment
    except HTTPException as e:
        raise e
