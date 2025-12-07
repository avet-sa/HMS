from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..dependencies.security import require_role
from ..db import models
from ..schemas.invoice import InvoiceResponse
from ..services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices")

@router.post("/{booking_id}", response_model=InvoiceResponse)
def generate_invoice(booking_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))):
    try:
        invoice = InvoiceService.generate_invoice(db, booking_id)
        return invoice
    except HTTPException as e:
        raise e
