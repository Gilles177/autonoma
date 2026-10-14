from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.models import ExceptionType
from src.ingestion.generator import generate_dataset
from src.rules.engine import detect_all
from src.rules.loop import apply_rules, automation_rate
from src.rules.models import Rule, RuleType
from src.rules.store import RuleStore

st.set_page_config(
    page_title="Autonoma — Autonomous Accounts Payable",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "dataset" not in st.session_state:
    st.session_state.dataset = generate_dataset(n_invoices=250, seed=42)

if "store" not in st.session_state:
    st.session_state.store = RuleStore(path=Path("data/rules.json"))

if "history" not in st.session_state:
    st.session_state.history = [
        {"step": "Baseline", "rate": None}
    ]

ds = st.session_state.dataset
store: RuleStore = st.session_state.store

raw_exceptions = detect_all(
    ds["invoices"], ds["suppliers"], ds["purchase_orders"], ds["goods_receipts"]
)
surviving, resolved = apply_rules(raw_exceptions, store.all())

rate_now = automation_rate(ds["invoices"], surviving)
baseline = automation_rate(ds["invoices"], raw_exceptions)

# Record history points on rule changes
if st.session_state.history[0]["rate"] is None:
    st.session_state.history[0]["rate"] = baseline
if (
    len(st.session_state.history) > 1
    and st.session_state.history[-1]["rate"] == rate_now
):
    pass
elif st.session_state.history[-1]["rate"] != rate_now:
    st.session_state.history.append(
        {"step": f"Step {len(st.session_state.history)}", "rate": rate_now}
    )


# ---------------------------------------------------------------------------
# Rule construction helpers (UI concerns)
# ---------------------------------------------------------------------------

def _mk_rule(
    rtype: RuleType,
    target: dict,
    payload: dict,
    source_ex: "object",
    rationale: str,
) -> Rule:
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
    t = ex.type
    sid = ex.detail.get("supplier_id")
    po = ex.detail.get("po_number")

    if t == ExceptionType.TAX_AMBIGUITY:
        expected = float(ex.detail.get("expected_vat", 0))
        actual = float(ex.detail.get("actual_vat", 0))
        return [
            (
                f"Use {expected*100:.1f}% going forward",
                lambda e: _mk_rule(
                    RuleType.SUPPLIER_VAT,
                    {"supplier_id": sid},
                    {"vat_rate": expected},
                    e,
                    f"Confirmed expected VAT {expected*100:.1f}% for {e.detail.get('supplier_name')}",
                ),
            ),
            (
                f"Keep {actual*100:.1f}% going forward",
                lambda e: _mk_rule(
                    RuleType.SUPPLIER_VAT,
                    {"supplier_id": sid},
                    {"vat_rate": actual},
                    e,
                    f"Confirmed actual VAT {actual*100:.1f}% for {e.detail.get('supplier_name')}",
                ),
            ),
        ]

    if t == ExceptionType.DUPLICATE:
        return [
            (
                "Block as duplicate",
                lambda e: _mk_rule(
                    RuleType.DUPLICATE_BLOCK,
                    {"invoice_id": e.invoice_id},
                    {},
                    e,
                    "Confirmed duplicate — blocked from payment",
                ),
            ),
            (
                "Not a duplicate — whitelist supplier",
                lambda e: _mk_rule(
                    RuleType.DUPLICATE_WHITELIST,
                    {"supplier_id": sid},
                    {},
                    e,
                    f"Legitimate split invoices from {e.detail.get('supplier_name')}",
                ),
            ),
        ]

    if t == ExceptionType.MISSING_PO:
        return [
            (
                "Exempt this supplier from PO requirement",
                lambda e: _mk_rule(
                    RuleType.PO_EXEMPTION,
                    {"supplier_id": sid},
                    {},
                    e,
                    f"{e.detail.get('supplier_name')} does not require a PO",
                ),
            ),
            (
                "Release this invoice once",
                lambda e: _mk_rule(
                    RuleType.INVOICE_RELEASED,
                    {"invoice_id": e.invoice_id},
                    {},
                    e,
                    "One-off release without PO",
                ),
            ),
        ]

    if t == ExceptionType.PRICE_MISMATCH:
        return [
            (
                "Accept invoice amount for this PO",
                lambda e: _mk_rule(
                    RuleType.PRICE_TOLERANCE,
                    {"po_number": po},
                    {},
                    e,
                    f"Invoice amount accepted for {po}",
                ),
            ),
            (
                "Use PO amount",
                lambda e: _mk_rule(
                    RuleType.PRICE_TOLERANCE,
                    {"po_number": po},
                    {},
                    e,
                    f"PO amount confirmed for {po}",
                ),
            ),
        ]

    if t == ExceptionType.IBAN_CHANGE:
        return [
            (
                "Approve new IBAN",
                lambda e: _mk_rule(
                    RuleType.IBAN_APPROVAL,
                    {"supplier_id": sid},
                    {"iban": e.detail.get("invoice_iban")},
                    e,
                    f"New IBAN approved for {e.detail.get('supplier_name')}",
                ),
            ),
            (
                "Reject — keep master IBAN",
                lambda e: _mk_rule(
                    RuleType.INVOICE_RELEASED,
                    {"invoice_id": e.invoice_id},
                    {},
                    e,
                    "IBAN change rejected — master IBAN retained",
                ),
            ),
        ]

    if t == ExceptionType.MISSING_GRN:
        return [
            (
                "Exempt this PO from GRN requirement",
                lambda e: _mk_rule(
                    RuleType.GRN_EXEMPTION,
                    {"po_number": po},
                    {},
                    e,
                    f"{po} does not require GRN",
                ),
            ),
            (
                "Release once",
                lambda e: _mk_rule(
                    RuleType.INVOICE_RELEASED,
                    {"invoice_id": e.invoice_id},
                    {},
                    e,
                    "One-off release without GRN",
                ),
            ),
        ]

    return [
        (
            "Release once",
            lambda e: _mk_rule(
                RuleType.INVOICE_RELEASED,
                {"invoice_id": e.invoice_id},
                {},
                e,
                "One-off release",
            ),
        )
    ]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("Autonoma")
st.caption(
    "Autonomous Accounts Payable for DACH — turn every invoice exception "
    "into a permanent rule."
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Automation Rate", f"{rate_now:.1f}%", f"+{rate_now - baseline:.1f}% vs baseline")
c2.metric("Open Exceptions", len(surviving))
c3.metric("Resolved by Rules", len(resolved))
c4.metric("Rules Learned", len(store))
c5.metric("Invoices Processed", len(ds["invoices"]))

st.divider()

tab_dash, tab_queue, tab_rules, tab_insights = st.tabs(
    ["Dashboard", "Exception Queue", "Rules Learned", "Supplier Insights"]
)


# ---------------------------------------------------------------------------
# Tab 1 — Dashboard
# ---------------------------------------------------------------------------

with tab_dash:
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Automation Rate Progression")
        hist_df = pd.DataFrame(st.session_state.history)
        fig = px.line(
            hist_df,
            x="step",
            y="rate",
            markers=True,
        )
        fig.update_yaxes(range=[0, 100], ticksuffix="%", title="Automation Rate")
        fig.update_xaxes(title="")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Exception Mix (open)")
        if surviving:
            counts = {}
            for ex in surviving:
                counts[ex.type.value] = counts.get(ex.type.value, 0) + 1
            mix = pd.DataFrame(
                sorted(counts.items(), key=lambda kv: -kv[1]),
                columns=["Type", "Count"],
            )
            st.dataframe(mix, use_container_width=True, hide_index=True)
        else:
            st.success("No open exceptions.")

    st.subheader("Rule Impact")
    if resolved:
        impact: dict[str, int] = {}
        for ex, rule in resolved:
            impact[rule.type.value] = impact.get(rule.type.value, 0) + 1
        impact_df = pd.DataFrame(
            sorted(impact.items(), key=lambda kv: -kv[1]),
            columns=["Rule Type", "Exceptions Auto-Resolved"],
        )
        st.dataframe(impact_df, use_container_width=True, hide_index=True)
    else:
        st.info("No rules yet. Go to Exception Queue and answer a question.")


# ---------------------------------------------------------------------------
# Tab 2 — Exception Queue
# ---------------------------------------------------------------------------

with tab_queue:
    st.subheader(f"Open Exceptions ({len(surviving)})")

    if not surviving:
        st.success("Every exception is resolved by rules. Automation rate is 100%.")
    else:
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_ex = sorted(
            surviving, key=lambda e: (sev_order.get(e.severity.value, 9), e.type.value)
        )

        sev_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        for i, ex in enumerate(sorted_ex):
            icon = sev_icons.get(ex.severity.value, "⚪")
            header = (
                f"{icon} **{ex.type.value.replace('_', ' ').title()}** — "
                f"{ex.detail.get('supplier_name', ex.invoice_id)}"
            )
            with st.expander(header, expanded=False):
                st.markdown(f"**Invoice:** `{ex.invoice_id}`")
                st.markdown(f"**Message:** {ex.message}")
                if ex.resolution_question:
                    st.markdown(f"**Question:** *{ex.resolution_question}*")

                options = _answer_options(ex)
                cols = st.columns(len(options))
                for j, (label, factory) in enumerate(options):
                    if cols[j].button(label, key=f"ans_{i}_{j}"):
                        rule = factory(ex)
                        store.add(rule)
                        store.save()
                        st.rerun()


# ---------------------------------------------------------------------------
# Tab 3 — Rules Learned
# ---------------------------------------------------------------------------

with tab_rules:
    st.subheader(f"Rules Learned ({len(store)})")

    if len(store) == 0:
        st.info("No rules yet.")
    else:
        rules = store.all()
        rules_df = pd.DataFrame(
            [
                {
                    "Rule ID": r.rule_id,
                    "Type": r.type.value,
                    "Target": ", ".join(f"{k}={v}" for k, v in r.target.items()),
                    "Rationale": r.rationale,
                    "Created": r.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for r in rules
            ]
        )
        st.dataframe(rules_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Remove a rule")
        to_remove = st.selectbox(
            "Select a rule to delete",
            options=[r.rule_id for r in rules],
            format_func=lambda rid: next(
                f"{rid} — {r.rationale}" for r in rules if r.rule_id == rid
            ),
        )
        if st.button("Delete rule"):
            store.remove(to_remove)
            store.save()
            st.rerun()

        st.divider()
        if st.button("Reset all rules"):
            store.clear()
            store.save()
            st.rerun()


# ---------------------------------------------------------------------------
# Tab 4 — Supplier Insights
# ---------------------------------------------------------------------------

with tab_insights:
    st.subheader("Where automation is leaking")

    if not surviving:
        st.success("No open exceptions to analyze.")
    else:
        by_supplier: dict[str, int] = {}
        for ex in surviving:
            name = ex.detail.get("supplier_name", "Unknown")
            by_supplier[name] = by_supplier.get(name, 0) + 1

        top = sorted(by_supplier.items(), key=lambda kv: -kv[1])[:15]
        df = pd.DataFrame(top, columns=["Supplier", "Open Exceptions"])

        fig = px.bar(
            df,
            x="Open Exceptions",
            y="Supplier",
            orientation="h",
            title="Top suppliers by open exceptions",
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Suppliers at the top of this list are where a rule, a master data fix, "
            "or a department conversation will unlock the most automation."
        )
