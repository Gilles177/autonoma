from __future__ import annotations

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from src.reports.sprint import SprintReport


def _safe(s: str) -> str:
    """fpdf2 core fonts are latin-1. Replace unsupported chars rather than crash."""
    return s.encode("latin-1", errors="replace").decode("latin-1")


class _ReportPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(34, 100, 160)
        self.cell(0, 10, "Autonoma - Automation Sprint Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 215, 230)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 150, 165)
        self.cell(0, 10, f"Autonoma  -  page {self.page_no()}", align="C")


def _section(pdf: FPDF, title: str) -> None:
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 40, 70)
    pdf.cell(0, 8, _safe(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(180, 200, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)


def _kv(pdf: FPDF, key: str, value: str) -> None:
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(70, 80, 95)
    pdf.cell(70, 6, _safe(key), new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(20, 30, 50)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, _safe(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(report: SprintReport) -> bytes:
    pdf = _ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(110, 120, 135)
    pdf.cell(
        0, 6,
        _safe(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}"),
        new_x=XPos.LMARGIN, new_y=YPos.NEXT,
    )
    pdf.ln(2)

    # ---------- Headline ----------
    _section(pdf, "Headline")
    _kv(pdf, "Invoices processed", str(report.invoice_count))
    _kv(pdf, "Baseline automation rate", f"{report.baseline_rate:.2f}%")
    _kv(pdf, "Current automation rate", f"{report.current_rate:.2f}%")
    _kv(pdf, "Improvement", f"{report.delta:+.2f} pp")
    _kv(pdf, "Rules learned this sprint", str(len(report.rules)))
    _kv(pdf, "Exceptions auto-resolved by rules", str(len(report.resolved)))
    _kv(pdf, "Open exceptions remaining", str(len(report.open_exceptions)))

    # ---------- Rules Learned ----------
    if report.rules:
        _section(pdf, "Rules Learned")
        for r in report.rules:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(34, 100, 160)
            pdf.cell(0, 6, _safe(r.rule_id), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(70, 80, 95)
            target = ", ".join(f"{k}={v}" for k, v in r.target.items()) or "-"
            pdf.multi_cell(
                0, 5,
                _safe(f"Type:     {r.type.value}"),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.multi_cell(
                0, 5,
                _safe(f"Target:   {target}"),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.set_text_color(20, 30, 50)
            pdf.multi_cell(
                0, 5,
                _safe(f"Rationale: {r.rationale}"),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )
            pdf.ln(2)

    # ---------- Exception mixes ----------
    def _mix(title: str, items) -> None:
        counts: dict[str, int] = {}
        for ex in items:
            counts[ex.type.value] = counts.get(ex.type.value, 0) + 1
        if not counts:
            return
        _section(pdf, title)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 45, 65)
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
            pdf.cell(
                0, 6, _safe(f"- {k}: {v}"),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )

    _mix("Exceptions Auto-Resolved", report.resolved)
    _mix("Remaining Leaks (Open Exceptions)", report.open_exceptions)

    # ---------- Top suppliers ----------
    if report.open_exceptions:
        _section(pdf, "Top Suppliers by Open Exceptions")
        supplier_counts: dict[str, int] = {}
        for ex in report.open_exceptions:
            name = ex.detail.get("supplier_name", "Unknown")
            supplier_counts[name] = supplier_counts.get(name, 0) + 1
        top = sorted(supplier_counts.items(), key=lambda kv: -kv[1])[:10]
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 45, 65)
        for name, count in top:
            pdf.cell(
                0, 6, _safe(f"- {name}: {count} open"),
                new_x=XPos.LMARGIN, new_y=YPos.NEXT,
            )

    return bytes(pdf.output())
