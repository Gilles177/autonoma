from __future__ import annotations

from datetime import timedelta
from typing import Iterable

from src.core.constants import (
    AMOUNT_TOLERANCE_FOR_DUP,
    DUPLICATE_WINDOW_DAYS,
    EXPECTED_VAT_BY_CATEGORY,
    PO_REQUIRED_THRESHOLD,
    PRICE_TOLERANCE_PCT,
)
from src.core.models import (
    ExceptionType,
    GoodsReceipt,
    Invoice,
    InvoiceException,
    PurchaseOrder,
    Severity,
    Supplier,
)


def _ex(
    invoice: Invoice,
    kind: ExceptionType,
    severity: Severity,
    message: str,
    question: str | None = None,
    detail: dict | None = None,
) -> InvoiceException:
    d = dict(detail or {})
    d.setdefault("supplier_id", invoice.supplier_id)
    d.setdefault("supplier_name", invoice.supplier_name)
    d.setdefault("currency", invoice.currency.value)
    d.setdefault("gross_amount", invoice.gross_amount)
    if invoice.po_number:
        d.setdefault("po_number", invoice.po_number)
    return InvoiceException(
        exception_id=f"{invoice.invoice_id}-{kind.value}",
        invoice_id=invoice.invoice_id,
        type=kind,
        severity=severity,
        message=message,
        resolution_question=question,
        detail=d,
    )


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

def detect_unknown_supplier(
    invoices: Iterable[Invoice], suppliers: dict[str, Supplier]
) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        if inv.supplier_id not in suppliers:
            out.append(
                _ex(
                    inv,
                    ExceptionType.UNKNOWN_SUPPLIER,
                    Severity.HIGH,
                    f"Supplier {inv.supplier_id} is not in the master data.",
                    "Should this supplier be created in the master, or is the invoice misrouted?",
                )
            )
    return out


def detect_duplicates(invoices: list[Invoice]) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    by_key: dict[tuple[str, str], list[Invoice]] = {}
    for inv in invoices:
        by_key.setdefault((inv.supplier_id, inv.invoice_number), []).append(inv)

    # Exact invoice-number duplicates
    for (sid, num), group in by_key.items():
        if len(group) > 1:
            first = group[0]
            for dup in group[1:]:
                out.append(
                    _ex(
                        dup,
                        ExceptionType.DUPLICATE,
                        Severity.CRITICAL,
                        f"Invoice number {num} from supplier {sid} already booked as {first.invoice_id}.",
                        f"Confirm: is {dup.invoice_id} a duplicate of {first.invoice_id}, or a legitimate second invoice?",
                        detail={"original_invoice_id": first.invoice_id, "match": "invoice_number"},
                    )
                )

    # Fuzzy duplicates: same supplier, same amount, close dates
    sorted_inv = sorted(invoices, key=lambda i: i.invoice_date)
    for i, inv in enumerate(sorted_inv):
        for other in sorted_inv[i + 1 :]:
            if other.supplier_id != inv.supplier_id:
                continue
            if other.invoice_date - inv.invoice_date > timedelta(days=DUPLICATE_WINDOW_DAYS):
                break
            if inv.invoice_number == other.invoice_number:
                continue  # already caught
            if inv.gross_amount == 0:
                continue
            delta = abs(other.gross_amount - inv.gross_amount) / inv.gross_amount
            if delta <= AMOUNT_TOLERANCE_FOR_DUP:
                out.append(
                    _ex(
                        other,
                        ExceptionType.DUPLICATE,
                        Severity.HIGH,
                        f"Amount matches {inv.invoice_id} within {delta*100:.2f}% and is {((other.invoice_date - inv.invoice_date).days)} days apart.",
                        f"Are {inv.invoice_id} and {other.invoice_id} the same obligation?",
                        detail={"original_invoice_id": inv.invoice_id, "match": "amount_date"},
                    )
                )
    return out


def detect_missing_po(invoices: Iterable[Invoice]) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        threshold = PO_REQUIRED_THRESHOLD.get(inv.currency.value, 500.0)
        if inv.po_number is None and inv.gross_amount > threshold:
            out.append(
                _ex(
                    inv,
                    ExceptionType.MISSING_PO,
                    Severity.MEDIUM,
                    f"Invoice has no PO and gross {inv.gross_amount:.2f} {inv.currency.value} exceeds {threshold:.0f}.",
                    "Is this invoice covered by a PO number that was not transmitted, or is it PO-free?",
                )
            )
    return out


def detect_price_mismatch(
    invoices: Iterable[Invoice], pos: dict[str, PurchaseOrder]
) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        if not inv.po_number:
            continue
        po = pos.get(inv.po_number)
        if po is None:
            continue
        if po.net_amount == 0:
            continue
        delta = (inv.net_amount - po.net_amount) / po.net_amount
        if abs(delta) > PRICE_TOLERANCE_PCT:
            severity = Severity.HIGH if abs(delta) > 0.1 else Severity.MEDIUM
            out.append(
                _ex(
                    inv,
                    ExceptionType.PRICE_MISMATCH,
                    severity,
                    f"Invoice net {inv.net_amount:.2f} vs PO {po.net_amount:.2f} ({delta*100:+.2f}%).",
                    f"Which amount is correct for {inv.po_number}, the PO or the invoice?",
                    detail={"po_amount": po.net_amount, "invoice_amount": inv.net_amount},
                )
            )
    return out


def detect_tax_ambiguity(
    invoices: Iterable[Invoice], suppliers: dict[str, Supplier]
) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        supplier = suppliers.get(inv.supplier_id)
        if supplier is None:
            continue
        expected = EXPECTED_VAT_BY_CATEGORY.get((supplier.country.value, supplier.category))
        if expected is None:
            continue
        if abs(inv.vat_rate - expected) > 1e-6:
            out.append(
                _ex(
                    inv,
                    ExceptionType.TAX_AMBIGUITY,
                    Severity.MEDIUM,
                    f"VAT rate {inv.vat_rate*100:.1f}% differs from expected {expected*100:.1f}% for {supplier.category} supplier in {supplier.country.value}.",
                    f"Should invoices from {supplier.name} be booked at {expected*100:.1f}% VAT going forward?",
                    detail={"expected_vat": expected, "actual_vat": inv.vat_rate},
                )
            )
    return out


def detect_missing_grn(
    invoices: Iterable[Invoice],
    pos: dict[str, PurchaseOrder],
    grns_by_po: dict[str, GoodsReceipt],
) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        if not inv.po_number:
            continue
        po = pos.get(inv.po_number)
        if po is None or not po.requires_grn:
            continue
        if inv.po_number not in grns_by_po:
            out.append(
                _ex(
                    inv,
                    ExceptionType.MISSING_GRN,
                    Severity.HIGH,
                    f"No goods receipt booked for {inv.po_number}.",
                    f"Has the delivery for {inv.po_number} been received but not booked, or not delivered yet?",
                    detail={"po_number": inv.po_number},
                )
            )
    return out


def detect_iban_change(
    invoices: Iterable[Invoice], suppliers: dict[str, Supplier]
) -> list[InvoiceException]:
    out: list[InvoiceException] = []
    for inv in invoices:
        supplier = suppliers.get(inv.supplier_id)
        if supplier is None:
            continue
        if inv.iban != supplier.iban:
            out.append(
                _ex(
                    inv,
                    ExceptionType.IBAN_CHANGE,
                    Severity.CRITICAL,
                    f"IBAN on invoice ({inv.iban}) differs from master ({supplier.iban}).",
                    f"Was {supplier.name}'s bank account legitimately changed? Do not pay until confirmed.",
                    detail={"master_iban": supplier.iban, "invoice_iban": inv.iban},
                )
            )
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def detect_all(
    invoices: list[Invoice],
    suppliers: list[Supplier],
    pos: list[PurchaseOrder],
    grns: list[GoodsReceipt],
) -> list[InvoiceException]:
    suppliers_by_id = {s.supplier_id: s for s in suppliers}
    pos_by_number = {p.po_number: p for p in pos}
    grns_by_po = {g.po_number: g for g in grns}

    results: list[InvoiceException] = []
    results += detect_unknown_supplier(invoices, suppliers_by_id)
    results += detect_duplicates(invoices)
    results += detect_missing_po(invoices)
    results += detect_price_mismatch(invoices, pos_by_number)
    results += detect_tax_ambiguity(invoices, suppliers_by_id)
    results += detect_missing_grn(invoices, pos_by_number, grns_by_po)
    results += detect_iban_change(invoices, suppliers_by_id)
    return results


def summarize(exceptions: list[InvoiceException]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ex in exceptions:
        counts[ex.type.value] = counts.get(ex.type.value, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def main() -> None:
    from src.ingestion.generator import generate_dataset

    ds = generate_dataset()
    exceptions = detect_all(
        ds["invoices"], ds["suppliers"], ds["purchase_orders"], ds["goods_receipts"]
    )

    inv_count = len(ds["invoices"])
    ex_count = len(exceptions)
    affected = len({e.invoice_id for e in exceptions})
    auto_rate = 100.0 * (inv_count - affected) / inv_count if inv_count else 0.0

    print(f"Invoices:          {inv_count}")
    print(f"Exceptions raised: {ex_count}")
    print(f"Invoices affected: {affected}")
    print(f"Baseline automation rate: {auto_rate:.2f}%")
    print()
    print("By type:")
    for k, v in summarize(exceptions).items():
        print(f"  {k:<18} {v}")
    print()
    print("Sample exceptions:")
    for ex in exceptions[:8]:
        print(f"  [{ex.severity.value.upper():<8}] {ex.type.value:<18} {ex.message}")


if __name__ == "__main__":
    main()
