<div align="center">

<a href="https://autonoma.streamlit.app/">
  <img src="assets/banner.svg" alt="Autonoma — Autonomous ERP Automation for DACH" width="900"/>
</a>

<br/>
<br/>

[![Live Demo](https://img.shields.io/badge/%E2%96%B6%20Live%20Demo-autonoma.streamlit.app-22D3EE?style=for-the-badge)](https://autonoma.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-4ADE80?style=for-the-badge)](LICENSE)

**Turn every invoice exception into a permanent rule — autonomous ERP automation for DACH enterprises.**

Made with ❤️ in Germany by **[Gilles Youtebo](https://github.com/Gilles177)**

</div>

---

## What is Autonoma?

Autonoma is an AI-native **Accounts Payable** cockpit for German and Swiss
enterprises. It ingests invoices, detects exceptions, learns a customer's
booking logic from their own history, and asks the **one decisive question**
that closes an exception permanently. Every answer becomes a rule. Every rule
removes a category of manual work forever — and the automation rate climbs
toward the target.

It is built around a single idea:

> **Every exception is a question. Every answer is a rule. Every rule removes a category of work permanently.**

---

## Live Demo

**[autonoma.streamlit.app →](https://autonoma.streamlit.app/)**

Click through the Exception Queue, answer a few questions, and watch the
automation rate move. Then download the **Sprint Report** as PDF.

---

## Why it matters

Finance and operations teams in the DACH region still spend enormous manual
effort on invoice exceptions:

- Missing purchase orders
- Price mismatches against the PO
- Ambiguous VAT rates (7% vs. 19% in DE; 2.6% / 3.8% / 8.1% in CH)
- Suspected duplicates
- Missing goods receipts
- Unannounced supplier IBAN changes

Autonoma treats each of these not as a ticket, but as a **learning
opportunity**. Six detectors run against every invoice; every exception
carries a resolution question; every answer is stored as a permanent rule.

---

## Features

| Feature | Description |
|---|---|
| **Exception engine** | Six detectors: duplicate, missing PO, price mismatch, tax ambiguity, missing GRN, IBAN change |
| **Rule-learning loop** | One decisive question per exception; the answer becomes a rule |
| **Automation sprint cockpit** | Baseline vs. current automation rate, rules learned, exceptions resolved |
| **Sprint report** | Downloadable as Markdown and PDF — the deliverable a consultant hands to the customer |
| **Bilingual UI** | English / German, toggled live |
| **DACH domain model** | EUR/CHF, German and Swiss VAT rules, IBAN formats, realistic supplier set |
| **Robotic HUD theme** | Dark control panel aesthetic with 13 CSS animations |

---

## Architecture
autonoma/
├── app/
│ └── autonoma.py # Streamlit entry point
├── src/
│ ├── core/ # Domain models, constants
│ ├── ingestion/ # Synthetic DACH invoice generator
│ ├── rules/ # Exception engine, rule store, learning loop
│ ├── reports/ # Sprint report (Markdown + PDF)
│ ├── i18n/ # EN / DE translations
│ └── ui/ # Robotic HUD theme
├── data/
│ └── samples/ # Sample datasets
├── assets/ # Logo and banner
└── requirements.txt

---

## Stack

- **Python 3.12**
- **Streamlit** — app framework
- **pandas** — data handling
- **Plotly** — charts
- **pydantic** — domain models
- **fpdf2** — PDF report generation

---

## Run locally

```bash
git clone https://github.com/Gilles177/autonoma.git
cd autonoma
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/autonoma.py

Open http://localhost:8501.

Roadmap
□ CSV / Excel / XRechnung / QR-bill invoice upload
□ PDF invoice extraction (OCR + LLM structured output)
□ Persistence backend (Postgres) for multi-user rule stores
□ ERP adapters: SAP, Oracle, Microsoft Dynamics
□ Supplier portal for answering questions directly
□ Multi-tenant customer workspace

License
MIT — see LICENSE.

<div align="center">

Made with ❤️ in Germany by Gilles Youtebo

</div> ```
