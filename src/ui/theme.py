from __future__ import annotations

import streamlit as st

ROBOTIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    /* Single coherent palette — every panel draws from these */
    --bg:         #0B1220;
    --bg-elev:    #111B2E;
    --bg-panel:   #16233A;
    --bg-card:    #1A2A44;
    --border:     #2A3A56;
    --border-hi:  #3B5077;

    --cyan:       #22D3EE;
    --cyan-soft:  #38BDF8;
    --green:      #34D399;
    --amber:      #FBBF24;
    --red:        #F87171;

    --text:       #E5EDF7;
    --text-dim:   #94A3B8;
    --text-mute:  #64748B;
}

/* ---------- App shell ---------- */
.stApp {
    background-color: var(--bg);
    background-image:
      radial-gradient(circle at 12% 8%, rgba(34,211,238,0.09), transparent 42%),
      radial-gradient(circle at 88% 92%, rgba(52,211,153,0.05), transparent 42%),
      linear-gradient(rgba(56,189,248,0.030) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,189,248,0.030) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 44px 44px, 44px 44px;
    background-attachment: fixed;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

/* ---------- Text base ---------- */
.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stMarkdown, .stMarkdown p {
    color: var(--text);
}
h1, h2 { color: var(--text) !important; letter-spacing: -0.02em; }
h3 {
    color: var(--cyan) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    opacity: 0.9;
}
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.06em;
}

/* ---------- HUD ---------- */
.hud {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 22px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: linear-gradient(180deg, var(--bg-panel), var(--bg-elev));
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 0 1px rgba(34,211,238,0.05), 0 8px 32px rgba(0,0,0,0.35);
    animation: fadeInUp 0.6s ease both;
}
.hud::after {
    content: '';
    position: absolute;
    top: 0;
    left: -60%;
    width: 60%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scan 5s linear infinite;
}
@keyframes scan {
    from { left: -60%; }
    to   { left: 100%; }
}
.hud-mark {
    font-size: 1.6rem;
    color: var(--cyan);
    text-shadow: 0 0 14px rgba(34,211,238,0.65);
    animation: markPulse 3s ease-in-out infinite;
}
@keyframes markPulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.55; }
}
.hud-body { flex: 1; }
.hud-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.24em;
    color: var(--text);
}
.hud-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    color: var(--text-dim);
    margin-top: 2px;
}
.hud-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    color: var(--green);
}
.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green);
    animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.4; transform: scale(0.7); }
}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--bg-card), var(--bg-panel));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 20px 14px 20px;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.55s ease both;
}
/* Staggered reveal for the 5 metric cards */
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) [data-testid="stMetric"] { animation-delay: 0.05s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) [data-testid="stMetric"] { animation-delay: 0.15s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="stMetric"] { animation-delay: 0.25s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(4) [data-testid="stMetric"] { animation-delay: 0.35s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(5) [data-testid="stMetric"] { animation-delay: 0.45s; }

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(34,211,238,0.45), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(34,211,238,0.55);
    box-shadow: 0 0 0 1px rgba(34,211,238,0.15), 0 10px 36px rgba(34,211,238,0.12);
    transform: translateY(-2px);
}
[data-testid="stMetric"]:hover::before { opacity: 1; }

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    text-shadow: 0 0 18px rgba(34,211,238,0.30);
    animation: valuePulse 3.6s ease-in-out infinite;
}
@keyframes valuePulse {
    0%, 100% { text-shadow: 0 0 18px rgba(34,211,238,0.30); }
    50%      { text-shadow: 0 0 26px rgba(34,211,238,0.55); }
}

[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 5px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 8px 14px;
    transition: all 0.25s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text);
    background: rgba(34,211,238,0.06);
}
.stTabs [aria-selected="true"] {
    background: rgba(34,211,238,0.12) !important;
    color: var(--cyan) !important;
    box-shadow: inset 0 0 0 1px rgba(34,211,238,0.40),
                0 0 18px rgba(34,211,238,0.20);
    animation: tabGlow 2.8s ease-in-out infinite;
}
@keyframes tabGlow {
    0%, 100% { box-shadow: inset 0 0 0 1px rgba(34,211,238,0.40), 0 0 14px rgba(34,211,238,0.15); }
    50%      { box-shadow: inset 0 0 0 1px rgba(34,211,238,0.65), 0 0 24px rgba(34,211,238,0.38); }
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.35);
    color: var(--cyan);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.2s;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: rgba(34,211,238,0.18);
    border-color: var(--cyan);
    box-shadow: 0 0 22px rgba(34,211,238,0.35);
    color: #FFFFFF;
}

/* ---------- Expander ---------- */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-panel) !important;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(34,211,238,0.40) !important;
    box-shadow: 0 0 0 1px rgba(34,211,238,0.12);
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span { color: var(--text) !important; }

/* ---------- Radio (language toggle) ---------- */
[role="radiogroup"] {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
}
[role="radiogroup"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.15em !important;
    color: var(--text-dim) !important;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}
[role="radiogroup"] label:hover { color: var(--text) !important; }
[role="radiogroup"] label:has(input:checked) {
    background: rgba(34,211,238,0.14);
    color: var(--cyan) !important;
    box-shadow: inset 0 0 0 1px rgba(34,211,238,0.35);
}
[role="radiogroup"] input { display: none; }

/* ---------- Dataframe — force dark, consistent with panels ---------- */
[data-testid="stDataFrame"],
[data-testid="stDataFrameResizable"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
    background: var(--bg-panel) !important;
}
[data-testid="stDataFrame"] * {
    background-color: transparent !important;
    color: var(--text) !important;
}
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] .gdg-header-cell {
    background-color: var(--bg-card) !important;
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.06em;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] .gdg-cell {
    border-color: var(--border) !important;
}

/* ---------- Select / Multiselect ---------- */
[data-baseweb="select"] > div,
[data-baseweb="popover"] {
    background-color: var(--bg-panel) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="menu"] li {
    color: var(--text) !important;
}
[data-baseweb="menu"] li:hover {
    background-color: rgba(34,211,238,0.10) !important;
}

/* ---------- Alerts (success / info / warning) — keep consistent ---------- */
[data-testid="stAlert"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px;
}

/* ---------- Toast ---------- */
[data-testid="stToast"] {
    background: linear-gradient(180deg, var(--bg-card), var(--bg-panel)) !important;
    border: 1px solid rgba(34,211,238,0.45) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan) !important;
    box-shadow: 0 8px 40px rgba(34,211,238,0.25) !important;
}
"""


def inject_theme() -> None:
    st.markdown(f"<style>{ROBOTIC_CSS}</style>", unsafe_allow_html=True)


def render_hud(tag: str, status: str) -> None:
    st.markdown(
        f"""
        <div class="hud">
          <div class="hud-mark">◆</div>
          <div class="hud-body">
            <div class="hud-name">AUTONOMA</div>
            <div class="hud-tag">{tag}</div>
          </div>
          <div class="hud-status">
            <span class="dot"></span>
            <span>{status}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
