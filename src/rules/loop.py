from __future__ import annotations

from src.core.models import ExceptionType, Invoice, InvoiceException
from src.rules.models import Rule, RuleType


# ---------------------------------------------------------------------------
# Rule matching
# ---------------------------------------------------------------------------

def _rule_matches(rule: Rule, ex: InvoiceException) -> bool:
    t = rule.type
    sid = ex.detail.get("supplier_id")
    po = ex.detail.get("po_number")

    if t == RuleType.SUPPLIER_VAT:
        return (
            ex.type == ExceptionType.TAX_AMBIGUITY
            and rule.target.get("supplier_id") == sid
            and abs(float(rule.payload.get("vat_rate", -1)) - float(ex.detail.get("actual_vat", -2))) < 1e-6
        )

    if t == RuleType.DUPLICATE_WHITELIST:
        return (
            ex.type == ExceptionType.DUPLICATE
            and rule.target.get("supplier_id") == sid
        )

    if t == RuleType.DUPLICATE_BLOCK:
        return (
            ex.type == ExceptionType.DUPLICATE
            and rule.target.get("invoice_id") == ex.invoice_id
        )

    if t == RuleType.PO_EXEMPTION:
        return (
            ex.type == ExceptionType.MISSING_PO
            and rule.target.get("supplier_id") == sid
        )

    if t == RuleType.PRICE_TOLERANCE:
        return (
            ex.type == ExceptionType.PRICE_MISMATCH
            and rule.target.get("po_number") == po
        )

    if t == RuleType.IBAN_APPROVAL:
        return (
            ex.type == ExceptionType.IBAN_CHANGE
            and rule.target.get("supplier_id") == sid
            and rule.payload.get("iban") == ex.detail.get("invoice_iban")
        )

    if t == RuleType.GRN_EXEMPTION:
        return (
            ex.type == ExceptionType.MISSING_GRN
            and rule.target.get("po_number") == po
        )

    if t == RuleType.INVOICE_RELEASED:
        return rule.target.get("invoice_id") == ex.invoice_id

    return False


def _matching_rule(ex: InvoiceException, rules: list[Rule]) -> Rule | None:
    for rule in rules:
        if _rule_matches(rule, ex):
            return rule
    return None


# ---------------------------------------------------------------------------
# Apply rules
# ---------------------------------------------------------------------------

def apply_rules(
    exceptions: list[InvoiceException], rules: list[Rule]
) -> tuple[list[InvoiceException], list[tuple[InvoiceException, Rule]]]:
    """Partition exceptions into (surviving, resolved)."""
    surviving: list[InvoiceException] = []
    resolved: list[tuple[InvoiceException, Rule]] = []

    for ex in exceptions:
        rule = _matching_rule(ex, rules)
        if rule is not None:
            ex.auto_resolved = True
            ex.resolved_by_rule_id = rule.rule_id
            resolved.append((ex, rule))
        else:
            surviving.append(ex)

    return surviving, resolved


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def automation_rate(invoices: list[Invoice], exceptions: list[InvoiceException]) -> float:
    if not invoices:
        return 0.0
    affected = {e.invoice_id for e in exceptions}
    return 100.0 * (len(invoices) - len(affected)) / len(invoices)
