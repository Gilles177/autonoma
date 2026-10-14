from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from src.core.models import Invoice, InvoiceException
from src.rules.loop import automation_rate
from src.rules.models import Rule


@dataclass
class SprintReport:
    generated_at: datetime
    invoice_count: int
    baseline_rate: float
    current_rate: float
    rules: list[Rule] = field(default_factory=list)
    resolved: list[InvoiceException] = field(default_factory=list)
    open_exceptions: list[InvoiceException] = field(default_factory=list)

    @property
    def delta(self) -> float:
        return self.current_rate - self.baseline_rate

    def _count_by_type(self, items: Iterable[InvoiceException]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for ex in items:
            counts[ex.type.value] = counts.get(ex.type.value, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    def _count_by_supplier(self, items: Iterable[InvoiceException]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for ex in items:
            name = ex.detail.get("supplier_name", "Unknown")
            counts[name] = counts.get(name, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1]))

    def to_markdown(self) -> str:
        lines: list[str] = []
        lines.append("# Autonoma — Automation Sprint Report")
        lines.append("")
        lines.append(f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")
        lines.append("## Headline")
        lines.append("")
        lines.append(f"- Invoices processed: **{self.invoice_count}**")
        lines.append(f"- Baseline automation rate: **{self.baseline_rate:.2f}%**")
        lines.append(f"- Current automation rate: **{self.current_rate:.2f}%**")
        lines.append(f"- Improvement: **{self.delta:+.2f} percentage points**")
        lines.append(f"- Rules learned this sprint: **{len(self.rules)}**")
        lines.append(
            f"- Exceptions auto-resolved by rules: **{len(self.resolved)}**"
        )
        lines.append(
            f"- Open exceptions remaining: **{len(self.open_exceptions)}**"
        )
        lines.append("")

        if self.rules:
            lines.append("## Rules Learned")
            lines.append("")
            lines.append("| Rule ID | Type | Target | Rationale |")
            lines.append("|---|---|---|---|")
            for r in self.rules:
                target = ", ".join(f"{k}={v}" for k, v in r.target.items()) or "—"
                lines.append(
                    f"| {r.rule_id} | {r.type.value} | {target} | {r.rationale} |"
                )
            lines.append("")

        resolved_mix = self._count_by_type(self.resolved)
        if resolved_mix:
            lines.append("## Exceptions Auto-Resolved")
            lines.append("")
            for k, v in resolved_mix.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        open_mix = self._count_by_type(self.open_exceptions)
        if open_mix:
            lines.append("## Remaining Leaks (Open Exceptions)")
            lines.append("")
            for k, v in open_mix.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        supplier_leaks = self._count_by_supplier(self.open_exceptions)
        if supplier_leaks:
            lines.append("## Top Suppliers by Open Exceptions")
            lines.append("")
            lines.append("| Supplier | Open Exceptions |")
            lines.append("|---|---|")
            for name, count in list(supplier_leaks.items())[:10]:
                lines.append(f"| {name} | {count} |")
            lines.append("")

        lines.append("## Next Sprint Priorities")
        lines.append("")
        if supplier_leaks:
            top = list(supplier_leaks.items())[:3]
            for name, count in top:
                lines.append(
                    f"- Work with the owner of **{name}** — {count} open exceptions. "
                    "One rule or one master-data fix unlocks all of them."
                )
        else:
            lines.append("- No open exceptions. All clear.")
        lines.append("")

        return "\n".join(lines)


def build_report(
    invoices: list[Invoice],
    baseline_exceptions: list[InvoiceException],
    open_exceptions: list[InvoiceException],
    resolved: list[tuple[InvoiceException, Rule]],
    rules: list[Rule],
) -> SprintReport:
    return SprintReport(
        generated_at=datetime.now(timezone.utc),
        invoice_count=len(invoices),
        baseline_rate=automation_rate(invoices, baseline_exceptions),
        current_rate=automation_rate(invoices, open_exceptions),
        rules=rules,
        resolved=[ex for ex, _ in resolved],
        open_exceptions=open_exceptions,
    )
