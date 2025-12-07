from datetime import datetime
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..db import models


class InvoiceService:
    @staticmethod
    def generate_invoice(db: Session, booking_id: int) -> models.Invoice:
        booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.final_bill is None:
            raise HTTPException(status_code=400, detail="Booking final bill not set")

        subtotal = Decimal(booking.final_bill)
        tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
        total = (subtotal + tax).quantize(Decimal('0.01'))

        invoice_number = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"

        invoice = models.Invoice(
            booking_id=booking_id,
            invoice_number=invoice_number,
            subtotal=subtotal,
            tax=tax,
            total=total,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice
