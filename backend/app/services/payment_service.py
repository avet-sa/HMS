from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db import models


class PaymentService:
    @staticmethod
    def create_payment(db: Session, booking_id: int, amount: Decimal, method: str, currency: Optional[str] = "USD") -> models.Payment:
        booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Only allow payments for checked-out bookings
        booking_status = booking.status.value if hasattr(booking.status, "value") else booking.status
        if booking_status != models.BookingStatus.CHECKED_OUT.value:
            raise HTTPException(status_code=400, detail="Payments allowed only for CHECKED_OUT bookings")

        # Create pending payment
        payment = models.Payment(
            booking_id=booking_id,
            amount=amount,
            currency=currency or "USD",
            method=method,
            status=models.Payment.PaymentStatus.PENDING.value,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def process_payment(db: Session, payment_id: int) -> models.Payment:
        payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment_status = payment.status.value if hasattr(payment.status, "value") else payment.status
        if payment_status == models.Payment.PaymentStatus.PAID.value:
            return payment

        # Ensure we don't exceed booking final bill
        booking = db.query(models.Booking).filter(models.Booking.id == payment.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Sum already PAID amounts
        paid_sum_q = db.query(func.coalesce(func.sum(models.Payment.amount), 0)).filter(
            models.Payment.booking_id == booking.id,
            models.Payment.status == models.Payment.PaymentStatus.PAID.value,
        )
        paid_sum = paid_sum_q.scalar() or 0
        try:
            paid_sum = Decimal(paid_sum)
        except Exception:
            paid_sum = Decimal(str(paid_sum))

        if booking.final_bill is None:
            raise HTTPException(status_code=400, detail="Booking final bill not set")

        if (paid_sum + Decimal(payment.amount)) > Decimal(booking.final_bill):
            raise HTTPException(status_code=400, detail="Processing this payment would exceed the booking final bill")

        payment.status = models.Payment.PaymentStatus.PAID.value
        payment.processed_at = datetime.now()
        db.commit()
        db.refresh(payment)
        
        # Auto-generate invoice if not already generated
        from .invoice_service import InvoiceService
        existing_invoice = db.query(models.Invoice).filter(
            models.Invoice.booking_id == booking.id
        ).first()
        if not existing_invoice:
            InvoiceService.generate_invoice(db, booking.id)
        
        return payment

    @staticmethod
    def fail_payment(db: Session, payment_id: int) -> models.Payment:
        payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment.status = models.Payment.PaymentStatus.FAILED.value
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def refund_payment(db: Session, payment_id: int) -> models.Payment:
        payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        payment_status = payment.status.value if hasattr(payment.status, "value") else payment.status
        if payment_status != models.Payment.PaymentStatus.PAID.value:
            raise HTTPException(status_code=400, detail="Only PAID payments can be refunded")

        payment.status = models.Payment.PaymentStatus.REFUNDED.value
        payment.refunded_at = datetime.now()
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def list_payments(db: Session, current_user: models.User) -> List[models.Payment]:
        """
        List payments with RBAC logic:
        - ADMIN/MANAGER: see all payments
        - REGULAR: see payments only for bookings they created (booking.created_by == current_user.id)
        """
        if current_user.permission_level in (models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER):
            # Admin/Manager can see all payments
            return db.query(models.Payment).all()
        else:
            # REGULAR users only see payments for bookings they created
            return db.query(models.Payment).join(
                models.Booking, models.Payment.booking_id == models.Booking.id
            ).filter(models.Booking.created_by == current_user.id).all()
