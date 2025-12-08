from decimal import Decimal
from datetime import datetime, date
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..db import models
from .payment_service import PaymentService


class RefundPolicyService:
    """Handle refund calculation and processing based on cancellation policies."""

    @staticmethod
    def get_default_policy(db: Session) -> models.CancellationPolicy:
        """Get the default (active) cancellation policy."""
        policy = db.query(models.CancellationPolicy).filter(
            models.CancellationPolicy.is_active == True
        ).first()
        
        if not policy:
            # Create a sensible default if none exists
            policy = models.CancellationPolicy(
                name="Standard",
                full_refund_days=7,
                partial_refund_days=2,
                partial_refund_percentage=Decimal("50"),
                is_active=True,
            )
            db.add(policy)
            db.commit()
            db.refresh(policy)
        
        return policy

    @staticmethod
    def calculate_refund_percentage(booking: models.Booking, policy: models.CancellationPolicy) -> Decimal:
        """Calculate refund percentage based on cancellation timing.
        
        Returns:
            Decimal: Refund percentage (0-100)
        """
        if not booking.cancelled_at or not booking.check_in:
            return Decimal("0")
        
        # Calculate days between cancellation and check-in
        cancel_date = booking.cancelled_at.date() if hasattr(booking.cancelled_at, 'date') else booking.cancelled_at
        days_before_checkin = (booking.check_in - cancel_date).days
        
        # Full refund if cancelled well in advance
        if days_before_checkin >= policy.full_refund_days:
            return Decimal("100")
        
        # Partial refund if within the partial refund window
        if days_before_checkin >= policy.partial_refund_days:
            return Decimal(policy.partial_refund_percentage)
        
        # No refund if cancelled too close to check-in
        return Decimal("0")

    @staticmethod
    def process_cancellation_refunds(db: Session, booking: models.Booking, policy_id: int = None) -> None:
        """Process refunds for a cancelled booking.
        
        Args:
            db: Database session
            booking: The cancelled booking
            policy_id: Optional cancellation policy ID; uses default if not provided
        """
        # Get the cancellation policy
        if policy_id:
            policy = db.query(models.CancellationPolicy).filter(
                models.CancellationPolicy.id == policy_id
            ).first()
            if not policy:
                raise HTTPException(status_code=404, detail="Cancellation policy not found")
        else:
            policy = RefundPolicyService.get_default_policy(db)
        
        # Calculate refund percentage
        refund_percentage = RefundPolicyService.calculate_refund_percentage(booking, policy)
        
        if refund_percentage == 0:
            # No refunds
            return
        
        # Get all PAID payments for this booking
        paid_payments = db.query(models.Payment).filter(
            models.Payment.booking_id == booking.id,
            models.Payment.status == models.Payment.PaymentStatus.PAID.value,
        ).all()
        
        # Process refunds proportionally
        for payment in paid_payments:
            refund_amount = Decimal(payment.amount) * (refund_percentage / Decimal("100"))
            
            if refund_amount > 0:
                # Create a refund payment record
                refund = models.Payment(
                    booking_id=booking.id,
                    amount=refund_amount,
                    currency=payment.currency,
                    method=payment.method,
                    status=models.Payment.PaymentStatus.REFUNDED.value,
                    refunded_at=datetime.now(),
                    reference=f"Refund for {payment.reference or f'Payment {payment.id}'}; Policy: {policy.name}",
                )
                db.add(refund)
        
        db.commit()
