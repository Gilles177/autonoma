from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RuleType(str, Enum):
    SUPPLIER_VAT = "supplier_vat"
    DUPLICATE_WHITELIST = "duplicate_whitelist"
    DUPLICATE_BLOCK = "duplicate_block"
    PO_EXEMPTION = "po_exemption"
    PRICE_TOLERANCE = "price_tolerance"
    IBAN_APPROVAL = "iban_approval"
    GRN_EXEMPTION = "grn_exemption"
    INVOICE_RELEASED = "invoice_released"


class Rule(BaseModel):
    rule_id: str
    type: RuleType
    target: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    source_exception_id: str | None = None
    source_question: str | None = None
    source_answer: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
