from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime


class InvoiceResponse(BaseModel):
    id: int
    booking_id: int
    invoice_number: str
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    issued_at: datetime
    model_config = ConfigDict(from_attributes=True)
