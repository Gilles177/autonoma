from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Currency(str, Enum):
    EUR = "EUR"
    CHF = "CHF"


class Country(str, Enum):
    DE = "DE"
    CH = "CH"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExceptionType(str, Enum):
    DUPLICATE = "duplicate"
    MISSING_PO = "missing_po"
    PRICE_MISMATCH = "price_mismatch"
    TAX_AMBIGUITY = "tax_ambiguity"
    MISSING_GRN = "missing_grn"
    IBAN_CHANGE = "iban_change"
    UNKNOWN_SUPPLIER = "unknown_supplier"


class Supplier(BaseModel):
    supplier_id: str
    name: str
    country: Country
    currency: Currency
    vat_id: str
    iban: str
    default_gl_account: str
    category: str  # "goods" or "services"


class PurchaseOrder(BaseModel):
    po_number: str
    supplier_id: str
    currency: Currency
    net_amount: float
    vat_rate: float
    issued_on: date
    requires_grn: bool = True


class GoodsReceipt(BaseModel):
    grn_number: str
    po_number: str
    received_on: date
    net_amount: float


class Invoice(BaseModel):
    invoice_id: str
    supplier_id: str
    supplier_name: str
    invoice_number: str
    invoice_date: date
    due_date: date
    currency: Currency
    net_amount: float
    vat_rate: float
    vat_amount: float
    gross_amount: float
    po_number: Optional[str] = None
    grn_number: Optional[str] = None
    iban: str
    description: str = ""
    gl_account: Optional[str] = None


class InvoiceException(BaseModel):
    exception_id: str
    invoice_id: str
    type: ExceptionType
    severity: Severity
    message: str
    resolution_question: Optional[str] = None
    detail: dict[str, Any] = Field(default_factory=dict)
