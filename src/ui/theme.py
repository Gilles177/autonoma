from __future__ import annotations

import streamlit as st

ROBOTIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg:         #06090D;
    --bg-elev:    #0D141B;
    --bg-panel:   #121A23;
    --border:     #1E2A37;
    --cyan:       #00E5FF;
    --green:      #00FF9C;
    --amber:      #FFB200;
    --red:        #FF3D5A;
    --text:       #DCE6F2;
    --text-dim:   #7A8A9A;
}

/* ---------- App shell ---------- */
.stApp {
    background-color: var(--bg);
    background-image:
      radial-gradient(circle at 12% 8%, rgba(0,229,255,0.10), transparent 40%),
      radial-gradient(circle at 88% 92%, rgba(0,255,156,0.06), transparent 40%),
      linear-gradient(rgba(0,229,255,0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.035) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 44px 44px, 44px 44px;
    background-attachment: fixed;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

/* ---------- Headings ---------- */
h1, h2 {
    color: var(--text) !important;
    letter-spacing: -0.02em;
}
h3 {
    color: var(--cyan) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.6rem !important;
    opacity: 0.85;
}

/* ---------- HUD ---------- */
.hud {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 22px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: linear-gradient(180deg, rgba(18,26,35,0.95), rgba(13,20,27,0.75));
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 0 1px rgba(0,229,255,0.06), 0 8px 40px rgba(0,0,0,0.4);
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
    text-shadow: 0 0 14px rgba(0,229,255,0.7);
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
    background: linear-gradient(180deg, rgba(18,26,35,0.9), rgba(13,20,27,0.6));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px 20px 14px 20px;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.35), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,229,255,0.45);
    box-shadow: 0 0 0 1px rgba(0,229,255,0.15), 0 10px 36px rgba(0,229,255,0.10);
    transform: translateY(-2px);
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    text-shadow: 0 0 20px rgba(0,229,255,0.28);
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

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(13,20,27,0.7);
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
    transition: all 0.2s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text);
    background: rgba(0,229,255,0.05);
}
.stTabs [aria-selected="true"] {
    background: rgba(0,229,255,0.10) !important;
    color: var(--cyan) !important;
    box-shadow: inset 0 0 0 1px rgba(0,229,255,0.35);
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
    background: rgba(0,229,255,0.06);
    border: 1px solid rgba(0,229,255,0.30);
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
    background: rgba(0,229,255,0.16);
    border-color: var(--cyan);
    box-shadow: 0 0 20px rgba(0,229,255,0.30);
    color: #FFFFFF;
}

/* ---------- Expander ---------- */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: rgba(13,20,27,0.55) !important;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(0,229,255,0.35) !important;
    box-shadow: 0 0 0 1px rgba(0,229,255,0.10);
}

/* ---------- Radio (lang toggle) ---------- */
[role="radiogroup"] {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    background: rgba(13,20,27,0.85);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
}
[role="radiogroup"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.15em !important;
    color: var(--text-dim);
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}
[role="radiogroup"] label:hover { color: var(--text); }
[role="radiogroup"] label[data-checked="true"],
[role="radiogroup"] label:has(input:checked) {
    background: rgba(0,229,255,0.12);
    color: var(--cyan) !important;
    box-shadow: inset 0 0 0 1px rgba(0,229,255,0.30);
}
[role="radiogroup"] input { display: none; }

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* ---------- Toast ---------- */
[data-testid="stToast"] {
    background: linear-gradient(180deg, rgba(18,26,35,0.98), rgba(13,20,27,0.92)) !important;
    border: 1px solid rgba(0,229,255,0.35) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan) !important;
    box-shadow: 0 8px 40px rgba(0,229,255,0.20) !important;
}

/* ---------- Caption ---------- */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.06em;
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
