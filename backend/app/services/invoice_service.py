from datetime import datetime
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from io import BytesIO
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..db import models
from ..utils.pagination import paginate, apply_sorting

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class InvoiceService:
    @staticmethod
    def list_invoices(db: Session, page: int = 1, page_size: int = 50, search: Optional[str] = None,
                     sort_by: Optional[str] = None, sort_order: str = "desc"):
        """List invoices with pagination and search"""
        query = db.query(models.Invoice)
        
        # Apply search filter
        if search:
            # Search by invoice number or booking ID
            try:
                booking_id = int(search)
                query = query.filter(
                    (models.Invoice.invoice_number.ilike(f"%{search}%")) |
                    (models.Invoice.booking_id == booking_id)
                )
            except ValueError:
                # Not a number, search only by invoice number
                query = query.filter(models.Invoice.invoice_number.ilike(f"%{search}%"))
        
        # Apply sorting (default to issued_at desc)
        if not sort_by:
            sort_by = "issued_at"
        query = apply_sorting(query, models.Invoice, sort_by, sort_order)
        
        # Apply pagination
        return paginate(query, page, page_size)
    
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

    @staticmethod
    def generate_invoice_pdf(db: Session, invoice_id: int) -> bytes:
        """Generate a PDF invoice document"""
        if not REPORTLAB_AVAILABLE:
            raise HTTPException(status_code=500, detail="PDF generation not available. Install reportlab.")
        
        invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        booking = db.query(models.Booking).filter(models.Booking.id == invoice.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"<b>INVOICE</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Invoice details
        invoice_info = Paragraph(f"""
            <b>Invoice Number:</b> {invoice.invoice_number}<br/>
            <b>Issue Date:</b> {invoice.issued_at.strftime('%Y-%m-%d %H:%M') if invoice.issued_at else 'N/A'}<br/>
            <b>Booking ID:</b> {booking.id}<br/>
            <b>Booking Number:</b> {booking.booking_number or 'N/A'}<br/>
        """, styles['Normal'])
        elements.append(invoice_info)
        elements.append(Spacer(1, 20))
        
        # Guest information
        guest_info = Paragraph(f"""
            <b>Guest Information:</b><br/>
            Name: {booking.guest.name if booking.guest else 'N/A'} {booking.guest.surname if booking.guest else ''}<br/>
            Email: {booking.guest.email if booking.guest else 'N/A'}<br/>
        """, styles['Normal'])
        elements.append(guest_info)
        elements.append(Spacer(1, 20))
        
        # Booking details table
        data = [
            ['Description', 'Quantity', 'Rate', 'Amount'],
            [f'Room Stay (Room #{booking.room.number if booking.room else "N/A"})', 
             str(booking.number_of_nights), 
             f'${booking.price_per_night}', 
             f'${invoice.subtotal}'],
            ['', '', 'Subtotal:', f'${invoice.subtotal}'],
            ['', '', 'Tax (10%):', f'${invoice.tax}'],
            ['', '', 'Total:', f'${invoice.total}'],
        ]
        
        table = Table(data, colWidths=[250, 80, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Footer
        footer = Paragraph("""
            <b>Thank you for your business!</b><br/>
            For any questions, please contact our front desk.
        """, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get the PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
