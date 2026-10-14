from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.models import ExceptionType
from src.i18n.translations import get_translator
from src.ingestion.generator import generate_dataset
from src.rules.engine import detect_all
from src.rules.loop import apply_rules, automation_rate
from src.rules.models import Rule, RuleType
from src.rules.store import RuleStore
from src.ui.theme import inject_theme, render_hud, render_rate_bar, render_ticker

st.set_page_config(
    page_title="Autonoma — Autonomous Accounts Payable",
    page_icon="◆",
    layout="wide",
)

inject_theme()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

if "dataset" not in st.session_state:
    st.session_state.dataset = generate_dataset(n_invoices=250, seed=42)

if "store" not in st.session_state:
    st.session_state.store = RuleStore(path=Path("data/rules.json"))

if "history" not in st.session_state:
    st.session_state.history = [{"step": "Baseline", "rate": None}]

if "toast" not in st.session_state:
    st.session_state.toast = None

ds = st.session_state.dataset
store: RuleStore = st.session_state.store

lang = st.session_state.lang
t = get_translator(lang)

raw_exceptions = detect_all(
    ds["invoices"], ds["suppliers"], ds["purchase_orders"], ds["goods_receipts"]
)
surviving, resolved = apply_rules(raw_exceptions, store.all())

rate_now = automation_rate(ds["invoices"], surviving)
baseline = automation_rate(ds["invoices"], raw_exceptions)

if st.session_state.history[0]["rate"] is None:
    st.session_state.history[0]["rate"] = baseline
if st.session_state.history[-1]["rate"] != rate_now:
    st.session_state.history.append(
        {"step": f"Step {len(st.session_state.history)}", "rate": rate_now}
    )

# ---------------------------------------------------------------------------
# Header — HUD + language toggle
# ---------------------------------------------------------------------------

head_left, head_right = st.columns([6, 1])
with head_left:
    render_hud(tag=t("hud.tag"), status=t("hud.status"))

render_ticker([
    "SYS::OK",
    "AGENTS::24",
    f"INVOICES::{len(ds['invoices'])}",
    f"RULES::{len(store)}",
    f"AUTOMATION::{rate_now:.1f}%",
    "LATENCY::42ms",
    "UPTIME::99.98%",
    "REGION::DACH",
    "MODE::AUTONOMOUS",
    "TARGET::ERP",
])
with head_right:
    choice = st.radio(
        "lang",
        options=["EN", "DE"],
        index=0 if lang == "EN" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="lang_radio",
    )
    if choice != lang:
        st.session_state.lang = choice
        st.rerun()

st.write("")
st.caption(t("app.caption"))

# ---------------------------------------------------------------------------
# Metric row
# ---------------------------------------------------------------------------

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    t("metric.automation_rate"),
    f"{rate_now:.1f}%",
    f"+{rate_now - baseline:.1f}% {t('metric.vs_baseline')}",
    help=t("metric.automation_rate_help"),
)
c2.metric(
    t("metric.open_exceptions"),
    len(surviving),
    help=t("metric.open_exceptions_help"),
)
c3.metric(
    t("metric.resolved"),
    len(resolved),
    help=t("metric.resolved_help"),
)
c4.metric(
    t("metric.rules"),
    len(store),
    help=t("metric.rules_help"),
)
c5.metric(
    t("metric.invoices"),
    len(ds["invoices"]),
    help=t("metric.invoices_help"),
)

st.write("")
render_rate_bar(rate=rate_now, target=95.0, label=t("metric.automation_rate"))
st.write("")

# ---------------------------------------------------------------------------
# Rule construction helpers
# ---------------------------------------------------------------------------

def _mk_rule(rtype: RuleType, target: dict, payload: dict, source_ex, rationale: str) -> Rule:
    return Rule(
        rule_id=f"RULE-{uuid.uuid4().hex[:8].upper()}",
        type=rtype,
        target=target,
        payload=payload,
        rationale=rationale,
        source_exception_id=source_ex.exception_id,
        source_question=source_ex.resolution_question,
        source_answer=rationale,
    )


def _answer_options(ex):
    t_ = ex.type
    sid = ex.detail.get("supplier_id")
    po = ex.detail.get("po_number")

    if t_ == ExceptionType.TAX_AMBIGUITY:
        expected = float(ex.detail.get("expected_vat", 0))
        actual = float(ex.detail.get("actual_vat", 0))
        return [
            (f"Use {expected*100:.1f}%",
             lambda e: _mk_rule(RuleType.SUPPLIER_VAT, {"supplier_id": sid}, {"vat_rate": expected}, e,
                                f"Confirmed VAT {expected*100:.1f}% for {e.detail.get('supplier_name')}")),
            (f"Keep {actual*100:.1f}%",
             lambda e: _mk_rule(RuleType.SUPPLIER_VAT, {"supplier_id": sid}, {"vat_rate": actual}, e,
                                f"Confirmed VAT {actual*100:.1f}% for {e.detail.get('supplier_name')}")),
        ]
    if t_ == ExceptionType.DUPLICATE:
        return [
            ("Block as duplicate",
             lambda e: _mk_rule(RuleType.DUPLICATE_BLOCK, {"invoice_id": e.invoice_id}, {}, e,
                                "Confirmed duplicate — blocked from payment")),
            ("Not a duplicate — whitelist supplier",
             lambda e: _mk_rule(RuleType.DUPLICATE_WHITELIST, {"supplier_id": sid}, {}, e,
                                f"Legitimate split invoices from {e.detail.get('supplier_name')}")),
        ]
    if t_ == ExceptionType.MISSING_PO:
        return [
            ("Exempt supplier from PO requirement",
             lambda e: _mk_rule(RuleType.PO_EXEMPTION, {"supplier_id": sid}, {}, e,
                                f"{e.detail.get('supplier_name')} does not require a PO")),
            ("Release invoice once",
             lambda e: _mk_rule(RuleType.INVOICE_RELEASED, {"invoice_id": e.invoice_id}, {}, e,
                                "One-off release without PO")),
        ]
    if t_ == ExceptionType.PRICE_MISMATCH:
        return [
            ("Accept invoice amount",
             lambda e: _mk_rule(RuleType.PRICE_TOLERANCE, {"po_number": po}, {}, e,
                                f"Invoice amount accepted for {po}")),
            ("Use PO amount",
             lambda e: _mk_rule(RuleType.PRICE_TOLERANCE, {"po_number": po}, {}, e,
                                f"PO amount confirmed for {po}")),
        ]
    if t_ == ExceptionType.IBAN_CHANGE:
        return [
            ("Approve new IBAN",
             lambda e: _mk_rule(RuleType.IBAN_APPROVAL, {"supplier_id": sid}, {"iban": e.detail.get("invoice_iban")}, e,
                                f"New IBAN approved for {e.detail.get('supplier_name')}")),
            ("Reject — keep master IBAN",
             lambda e: _mk_rule(RuleType.INVOICE_RELEASED, {"invoice_id": e.invoice_id}, {}, e,
                                "IBAN change rejected — master IBAN retained")),
        ]
    if t_ == ExceptionType.MISSING_GRN:
        return [
            ("Exempt PO from GRN",
             lambda e: _mk_rule(RuleType.GRN_EXEMPTION, {"po_number": po}, {}, e,
                                f"{po} does not require GRN")),
            ("Release once",
             lambda e: _mk_rule(RuleType.INVOICE_RELEASED, {"invoice_id": e.invoice_id}, {}, e,
                                "One-off release without GRN")),
        ]
    return [
        ("Release once",
         lambda e: _mk_rule(RuleType.INVOICE_RELEASED, {"invoice_id": e.invoice_id}, {}, e,
                            "One-off release")),
    ]


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_dash, tab_queue, tab_rules, tab_insights, tab_report = st.tabs([
    t("tab.dashboard"), t("tab.queue"), t("tab.rules"), t("tab.insights"), t("tab.report"),
])


# ---------- Dashboard ----------
with tab_dash:
    left, right = st.columns([2, 1])
    with left:
        st.subheader(t("dash.progression"))
        hist_df = pd.DataFrame(st.session_state.history)
        fig = px.line(hist_df, x="step", y="rate", markers=True)
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
        fig.update_xaxes(title="")
        fig.update_traces(line=dict(color="#00E5FF", width=3), marker=dict(size=9, color="#00FF9C"))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#DCE6F2", family="JetBrains Mono"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader(t("dash.mix"))
        if surviving:
            counts: dict[str, int] = {}
            for ex in surviving:
                counts[ex.type.value] = counts.get(ex.type.value, 0) + 1
            mix = pd.DataFrame(sorted(counts.items(), key=lambda kv: -kv[1]), columns=["Type", "Count"])
            st.dataframe(mix, use_container_width=True, hide_index=True)
        else:
            st.success(t("dash.no_open"))

    st.subheader(t("dash.rule_impact"))
    if resolved:
        impact: dict[str, int] = {}
        for ex, rule in resolved:
            impact[rule.type.value] = impact.get(rule.type.value, 0) + 1
        st.dataframe(
            pd.DataFrame(sorted(impact.items(), key=lambda kv: -kv[1]),
                         columns=["Rule Type", "Auto-Resolved"]),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info(t("dash.rule_impact_empty"))


# ---------- Exception Queue ----------
with tab_queue:
    st.subheader(f"{t('queue.title')} · {len(surviving)}")
    if not surviving:
        st.success(t("queue.empty"))
    else:
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_ex = sorted(surviving, key=lambda e: (sev_order.get(e.severity.value, 9), e.type.value))
        sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        for i, ex in enumerate(sorted_ex):
            icon = sev_icons.get(ex.severity.value, "⚪")
            header = (
                f"{icon} {ex.type.value.replace('_', ' ').title()} — "
                f"{ex.detail.get('supplier_name', ex.invoice_id)}"
            )
            with st.expander(header, expanded=False):
                st.markdown(f"**{t('queue.invoice')}:** `{ex.invoice_id}`")
                st.markdown(f"**{t('queue.message')}:** {ex.message}")
                if ex.resolution_question:
                    st.markdown(f"**{t('queue.question')}:** *{ex.resolution_question}*")
                options = _answer_options(ex)
                cols = st.columns(len(options))
                for j, (label, factory) in enumerate(options):
                    if cols[j].button(label, key=f"ans_{i}_{j}"):
                        rule = factory(ex)
                        store.add(rule)
                        store.save()
                        st.toast(f"✓ {t('toast.rule_learned')}: {rule.rationale}")
                        st.rerun()


# ---------- Rules Learned ----------
with tab_rules:
    st.subheader(f"{t('rules.title')} · {len(store)}")
    if len(store) == 0:
        st.info(t("rules.empty"))
    else:
        rules = store.all()
        st.dataframe(
            pd.DataFrame([
                {
                    t("rules.col_id"): r.rule_id,
                    t("rules.col_type"): r.type.value,
                    t("rules.col_target"): ", ".join(f"{k}={v}" for k, v in r.target.items()),
                    t("rules.col_rationale"): r.rationale,
                    t("rules.col_created"): r.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for r in rules
            ]),
            use_container_width=True, hide_index=True,
        )
        st.divider()
        st.subheader(t("rules.remove_title"))
        to_remove = st.selectbox(
            t("rules.col_id"),
            options=[r.rule_id for r in rules],
            format_func=lambda rid: next(f"{rid} — {r.rationale}" for r in rules if r.rule_id == rid),
        )
        if st.button(t("rules.remove_btn")):
            store.remove(to_remove)
            store.save()
            st.toast(f"✓ {t('toast.rule_removed')}")
            st.rerun()

        st.divider()
        if st.button(t("rules.reset_btn")):
            store.clear()
            store.save()
            st.toast(f"✓ {t('toast.rules_reset')}")
            st.rerun()


# ---------- Supplier Insights ----------
with tab_insights:
    st.subheader(t("insights.title"))
    if not surviving:
        st.success(t("insights.empty"))
    else:
        by_supplier: dict[str, int] = {}
        for ex in surviving:
            name = ex.detail.get("supplier_name", "Unknown")
            by_supplier[name] = by_supplier.get(name, 0) + 1
        top = sorted(by_supplier.items(), key=lambda kv: -kv[1])[:15]
        df = pd.DataFrame(top, columns=["Supplier", "Open Exceptions"])
        fig = px.bar(df, x="Open Exceptions", y="Supplier", orientation="h",
                     title=t("insights.chart_title"))
        fig.update_traces(marker_color="#00E5FF")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#DCE6F2", family="JetBrains Mono"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(t("insights.caption"))


# ---------- Sprint Report ----------
with tab_report:
    from src.reports.sprint import build_report

    st.subheader(t("report.title"))
    st.caption(t("report.caption"))

    report = build_report(
        invoices=ds["invoices"],
        baseline_exceptions=raw_exceptions,
        open_exceptions=surviving,
        resolved=resolved,
        rules=store.all(),
    )

    cA, cB, cC, cD = st.columns(4)
    cA.metric(t("report.baseline"), f"{report.baseline_rate:.1f}%")
    cB.metric(t("report.current"), f"{report.current_rate:.1f}%", f"{report.delta:+.1f}%")
    cC.metric(t("report.rules_learned"), len(report.rules))
    cD.metric(t("report.resolved"), len(report.resolved))

    st.divider()

    from src.reports.pdf import build_pdf

    md = report.to_markdown()
    pdf_bytes = build_pdf(report)
    stamp = report.generated_at.strftime("%Y%m%d-%H%M")

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label="Download Markdown",
            data=md,
            file_name=f"autonoma-sprint-{stamp}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with dl2:
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"autonoma-sprint-{stamp}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown(md)
# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="autonoma-footer">
      <div class="autonoma-footer-line"></div>
      <div class="autonoma-footer-tagline">{t('footer.tagline')}</div>
      <div class="autonoma-footer-by">{t('footer.made_by')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
