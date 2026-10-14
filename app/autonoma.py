import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Autonoma — Autonomous Accounts Payable",
    page_icon="🤖",
    layout="wide",
)

st.title("Autonoma")
st.caption(
    "Autonomous Accounts Payable for DACH — invoice exceptions, rule learning, "
    "automation-rate tracking, and customer resolution workflows."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Automation Rate", "87.4%", "+4.2%")
col2.metric("Open Exceptions", "143", "-18")
col3.metric("Invoices Processed", "12,480", "+1,204")
col4.metric("Manual Touches Avoided", "9,312", "+812")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Automation Rate Trend")
    df = pd.DataFrame(
        {
            "Week": ["W1", "W2", "W3", "W4", "W5", "W6"],
            "Automation Rate": [72, 76, 79, 82, 85, 87.4],
        }
    )
    fig = px.line(
        df,
        x="Week",
        y="Automation Rate",
        markers=True,
        title="Automation rate after go-live",
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top Exception Causes")
    exceptions = pd.DataFrame(
        {
            "Cause": [
                "Missing PO",
                "Price mismatch",
                "Tax code ambiguity",
                "Duplicate suspicion",
                "Missing GRN",
            ],
            "Count": [42, 31, 27, 22, 21],
        }
    )
    st.dataframe(exceptions, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Exception Workbench")
st.info(
    "Next milestone: upload invoices, extract fields, detect exceptions, "
    "ask the customer one decisive question, and turn the answer into a permanent rule."
)
