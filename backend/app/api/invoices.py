from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..dependencies.security import require_role
from ..db import models
from ..schemas.invoice import InvoiceResponse
from ..services.invoice_service import InvoiceService
from ..utils.pagination import PaginatedResponse

router = APIRouter(prefix="/invoices")

@router.get("/", response_model=PaginatedResponse[InvoiceResponse])
def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by invoice number or booking ID"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.PermissionLevel.REGULAR, models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))
):
    """List all invoices (accessible to all authenticated users)"""
    return InvoiceService.list_invoices(db, page, page_size, search, sort_by, sort_order)

@router.post("/{booking_id}", response_model=InvoiceResponse)
def generate_invoice(booking_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER))):
    try:
        invoice = InvoiceService.generate_invoice(db, booking_id)
        return invoice
    except HTTPException as e:
        raise e

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role(models.PermissionLevel.REGULAR, models.PermissionLevel.MANAGER, models.PermissionLevel.ADMIN))):
    """Generate and download invoice as PDF"""
    try:
        pdf_bytes = InvoiceService.generate_invoice_pdf(db, invoice_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
