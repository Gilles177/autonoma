# Autonoma

**Autonomous Accounts Payable for DACH.**

Autonoma is an AI-native accounts payable cockpit. It ingests invoices, detects
exceptions, learns a customer's booking logic from history, asks the one question
that closes an exception permanently, and tracks the automation rate toward target.

## Why

Finance and operations teams still spend enormous manual effort on invoice
exceptions: missing POs, price mismatches, tax ambiguity, duplicate suspicion,
missing goods receipts. Autonoma treats these not as tickets, but as learning
opportunities — every resolved exception becomes a permanent rule.

## Roadmap

1. Invoice ingestion (CSV, Excel, later PDF, XRechnung, QR-bill)
2. Exception engine (duplicate, missing PO, price mismatch, tax, GRN)
3. Rule learning loop (ask once, apply forever)
4. Automation sprint cockpit (automation rate, leakage, supplier-level root cause)
5. Customer question generator (turn exceptions into decisive questions)
6. ERP integration adapters (SAP, Oracle, Microsoft Dynamics)

## Stack

- Python
- Streamlit
- pandas
- Plotly
- pydantic

## Run locally

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/autonoma.py
