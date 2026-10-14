from __future__ import annotations

import base64

import streamlit as st

# ---------------------------------------------------------------------------
# SVG logo — hexagon frame with circuit "A" (as data URI so Streamlit keeps it)
# ---------------------------------------------------------------------------

_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <defs>
    <linearGradient id="ag" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#7DD3FC"/>
      <stop offset="100%" stop-color="#22D3EE"/>
    </linearGradient>
    <linearGradient id="ags" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0.10"/>
    </linearGradient>
  </defs>
  <path d="M24 2.5 L42 12.5 L42 35.5 L24 45.5 L6 35.5 L6 12.5 Z"
        fill="url(#ags)" stroke="url(#ag)" stroke-width="1.6" stroke-linejoin="round"/>
  <path d="M15 34 L24 14 L33 34" fill="none" stroke="url(#ag)"
        stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M19.5 27.5 L28.5 27.5" fill="none" stroke="url(#ag)"
        stroke-width="2.0" stroke-linecap="round"/>
  <circle cx="24" cy="14" r="1.7" fill="#E0F2FE"/>
  <circle cx="15" cy="34" r="1.7" fill="#E0F2FE"/>
  <circle cx="33" cy="34" r="1.7" fill="#E0F2FE"/>
</svg>"""

LOGO_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(
    _LOGO_SVG.encode("utf-8")
).decode("ascii")


ROBOTIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg:         #16223A;
    --bg-elev:    #1C2A45;
    --bg-panel:   #233553;
    --bg-card:    #2A3E5E;
    --bg-hover:   #31466A;

    --border:     #3A5178;
    --border-hi:  #4B6690;

    --cyan:       #38BDF8;
    --cyan-soft:  #7DD3FC;
    --green:      #4ADE80;
    --amber:      #FBBF24;
    --red:        #FB7185;

    --text:       #F1F5FB;
    --text-dim:   #B4C2D6;
    --text-mute:  #7C8DA6;
}

/* ---------- App shell ---------- */
.stApp {
    background-color: var(--bg);
    background-image:
      radial-gradient(circle at 12% 8%, rgba(56,189,248,0.10), transparent 45%),
      radial-gradient(circle at 88% 92%, rgba(74,222,128,0.06), transparent 45%),
      linear-gradient(rgba(56,189,248,0.032) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56,189,248,0.032) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 46px 46px, 46px 46px;
    background-attachment: fixed;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 15.5px;
}

[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

/* ---------- Base text ---------- */
.stApp, .stApp p, .stApp span, .stApp div, .stApp label,
.stMarkdown, .stMarkdown p {
    color: var(--text);
    font-size: 15px;
    line-height: 1.55;
}

h1 { color: var(--text) !important; font-size: 2.1rem !important; letter-spacing: -0.02em; }
h2 { color: var(--text) !important; font-size: 1.45rem !important; letter-spacing: -0.02em; }

h3 {
    color: var(--cyan-soft) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.90rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    position: relative;
    display: inline-block;
    background: linear-gradient(100deg,
        var(--cyan) 0%, var(--cyan) 40%,
        #E0F2FE 50%,
        var(--cyan) 60%, var(--cyan) 100%);
    background-size: 250% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmerSweep 6s ease-in-out infinite;
}
@keyframes shimmerSweep {
    0%   { background-position: 100% 0; }
    50%  { background-position: 0 0; }
    100% { background-position: 100% 0; }
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    letter-spacing: 0.05em;
}

/* ---------- HUD ---------- */
.hud {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 14px 22px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: linear-gradient(180deg, var(--bg-panel), var(--bg-elev));
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 0 1px rgba(56,189,248,0.05), 0 10px 36px rgba(0,0,0,0.30);
}
.hud::after {
    content: '';
    position: absolute;
    top: 0; left: -60%;
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    animation: scan 5s linear infinite;
}
@keyframes scan {
    from { left: -60%; }
    to   { left: 100%; }
}

.hud-logo {
    position: relative;
    width: 52px; height: 52px;
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
.autonoma-logo {
    width: 52px; height: 52px;
    filter: drop-shadow(0 0 10px rgba(56,189,248,0.60));
}
.hud-orbit {
    position: absolute; inset: 0;
    animation: logoOrbit 8s linear infinite;
    pointer-events: none;
}
.hud-orbit::before {
    content: '';
    position: absolute;
    top: -3px; left: 50%;
    width: 6px; height: 6px;
    margin-left: -3px;
    border-radius: 50%;
    background: var(--cyan-soft);
    box-shadow: 0 0 12px var(--cyan);
}
@keyframes logoOrbit {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}

.hud-body { flex: 1; min-width: 0; }
.hud-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.24em;
    color: var(--text);
    line-height: 1.1;
}
.hud-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.20em;
    color: var(--text-dim);
    margin-top: 4px;
}
.hud-status {
    display: flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.80rem;
    letter-spacing: 0.16em;
    color: var(--green);
    white-space: nowrap;
}
.dot {
    width: 9px; height: 9px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 12px var(--green);
    animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.45; transform: scale(0.7); }
}

/* Ticker — separate element, no mask, no overlay */
.hud-ticker {
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg-elev);
    margin-top: 10px;
    padding: 8px 0;
    overflow: hidden;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.12em;
    color: var(--text-dim);
    white-space: nowrap;
}
.hud-ticker-track {
    display: inline-block;
    padding-left: 100%;
    animation: tickerScroll 45s linear infinite;
}
.hud-ticker-track span { color: var(--cyan-soft); margin: 0 8px; }
@keyframes tickerScroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-100%); }
}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--bg-card), var(--bg-panel));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px 16px 22px;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.55s ease both;
}
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) [data-testid="stMetric"] { animation-delay: 0.05s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) [data-testid="stMetric"] { animation-delay: 0.15s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) [data-testid="stMetric"] { animation-delay: 0.25s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(4) [data-testid="stMetric"] { animation-delay: 0.35s; }
[data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(5) [data-testid="stMetric"] { animation-delay: 0.45s; }

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 15px;
    padding: 1px;
    background: conic-gradient(from 0deg,
        transparent 0deg, transparent 300deg,
        var(--cyan) 340deg, transparent 360deg);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
            mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s;
    animation: borderTrace 3s linear infinite;
    pointer-events: none;
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
@keyframes borderTrace { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

[data-testid="stMetric"]:hover {
    border-color: rgba(56,189,248,0.45);
    box-shadow: 0 0 0 1px rgba(56,189,248,0.15), 0 12px 40px rgba(56,189,248,0.14);
    transform: translateY(-2px);
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan-soft) !important;
    font-weight: 700 !important;
    font-size: 2.15rem !important;
    letter-spacing: -0.02em;
    text-shadow: 0 0 18px rgba(56,189,248,0.35);
    animation: valuePulse 3.6s ease-in-out infinite;
}
@keyframes valuePulse {
    0%, 100% { text-shadow: 0 0 18px rgba(56,189,248,0.30); }
    50%      { text-shadow: 0 0 28px rgba(56,189,248,0.60); }
}

[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ---------- Rate bar ---------- */
.rate-bar-wrap {
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 6px;
}
.rate-bar-label {
    display: flex; justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.14em;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 10px;
}
.rate-bar-label .val { color: var(--cyan-soft); font-weight: 700; }
.rate-bar-track {
    height: 10px; border-radius: 999px;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.14);
    overflow: hidden;
}
.rate-bar-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #22D3EE 0%, #7DD3FC 50%, #4ADE80 100%);
    box-shadow: 0 0 14px rgba(56,189,248,0.55);
    transform-origin: left;
    animation: barGrow 1.4s cubic-bezier(0.22, 1, 0.36, 1) both;
    position: relative; overflow: hidden;
}
.rate-bar-fill::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: translateX(-100%);
    animation: barShine 2.8s ease-in-out infinite;
}
@keyframes barGrow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes barShine {
    0%   { transform: translateX(-100%); }
    60%  { transform: translateX(100%); }
    100% { transform: translateX(100%); }
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
    font-size: 12.5px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    padding: 10px 16px;
    transition: all 0.25s;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text); background: rgba(56,189,248,0.08); }
.stTabs [aria-selected="true"] {
    background: rgba(56,189,248,0.14) !important;
    color: var(--cyan-soft) !important;
    animation: tabGlow 2.8s ease-in-out infinite;
}
@keyframes tabGlow {
    0%, 100% { box-shadow: inset 0 0 0 1px rgba(56,189,248,0.40), 0 0 14px rgba(56,189,248,0.18); }
    50%      { box-shadow: inset 0 0 0 1px rgba(56,189,248,0.65), 0 0 26px rgba(56,189,248,0.42); }
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.38);
    color: var(--cyan-soft);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    border-radius: 8px;
    padding: 10px 18px;
    transition: all 0.22s;
    position: relative;
    overflow: hidden;
}
.stButton > button::after, .stDownloadButton > button::after {
    content: '';
    position: absolute; top: 0; left: -60%;
    width: 40%; height: 100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: skewX(-20deg);
    opacity: 0;
    pointer-events: none;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: rgba(56,189,248,0.22);
    border-color: var(--cyan-soft);
    box-shadow: 0 0 24px rgba(56,189,248,0.40);
    color: #FFFFFF;
}
.stButton > button:hover::after, .stDownloadButton > button:hover::after {
    opacity: 1;
    animation: shineSweep 0.9s ease-out;
}
@keyframes shineSweep { from { left: -60%; } to { left: 130%; } }

/* ---------- Expander ---------- */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-panel) !important;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(56,189,248,0.40) !important;
    box-shadow: 0 0 0 1px rgba(56,189,248,0.12);
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span { color: var(--text) !important; font-size: 14.5px; }

/* ---------- Radio (language toggle) ---------- */
[role="radiogroup"] {
    display: flex; justify-content: flex-end; gap: 4px;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
}
[role="radiogroup"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    letter-spacing: 0.14em !important;
    color: var(--text-dim) !important;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}
[role="radiogroup"] label:hover { color: var(--text) !important; }
[role="radiogroup"] label:has(input:checked) {
    background: rgba(56,189,248,0.16);
    color: var(--cyan-soft) !important;
    box-shadow: inset 0 0 0 1px rgba(56,189,248,0.38);
}
[role="radiogroup"] input { display: none; }

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
    background: var(--bg-panel) !important;
    font-size: 14.5px !important;
}
[data-testid="stDataFrame"] * {
    background-color: transparent !important;
    color: var(--text) !important;
    font-size: 14.5px !important;
}
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] .gdg-header-cell {
    background-color: var(--bg-card) !important;
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border) !important;
}

/* ---------- Select / menu ---------- */
[data-baseweb="select"] > div, [data-baseweb="popover"] {
    background-color: var(--bg-panel) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-size: 14.5px !important;
}
[data-baseweb="menu"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="menu"] li { color: var(--text) !important; font-size: 14.5px; }
[data-baseweb="menu"] li:hover { background-color: rgba(56,189,248,0.12) !important; }

/* ---------- Alerts ---------- */
[data-testid="stAlert"] {
    background-color: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 12px;
    font-size: 14.5px;
}

/* ---------- Toast ---------- */
[data-testid="stToast"] {
    background: linear-gradient(180deg, var(--bg-card), var(--bg-panel)) !important;
    border: 1px solid rgba(56,189,248,0.45) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--cyan-soft) !important;
    font-size: 13px !important;
    box-shadow: 0 8px 40px rgba(56,189,248,0.28) !important;
}

/* ---------- Background particles ---------- */
.stApp::before, .stApp::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    filter: blur(1px);
}
.stApp::before {
    width: 4px; height: 4px;
    left: 18%; bottom: -10px;
    background: rgba(125,211,252,0.55);
    box-shadow:
        120px 0 0 rgba(125,211,252,0.35),
        340px 20px 0 rgba(56,189,248,0.45),
        620px -10px 0 rgba(125,211,252,0.40),
        880px 30px 0 rgba(56,189,248,0.30),
        1180px 0 0 rgba(125,211,252,0.45);
    animation: floatUp 22s linear infinite;
}
.stApp::after {
    width: 3px; height: 3px;
    left: 42%; bottom: -10px;
    background: rgba(74,222,128,0.45);
    box-shadow:
        200px 40px 0 rgba(74,222,128,0.30),
        460px -20px 0 rgba(125,211,252,0.35),
        720px 20px 0 rgba(74,222,128,0.30),
        980px 0 0 rgba(125,211,252,0.30);
    animation: floatUp 30s linear infinite;
    animation-delay: -6s;
}
@keyframes floatUp {
    from { transform: translateY(0); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    to   { transform: translateY(-110vh); opacity: 0; }
}
"""


def inject_theme() -> None:
    st.markdown(f"<style>{ROBOTIC_CSS}</style>", unsafe_allow_html=True)


def render_hud(tag: str, status: str) -> None:
    st.markdown(
        f"""
        <div class="hud">
          <div class="hud-logo">
            <img src="{LOGO_DATA_URI}" class="autonoma-logo" alt="Autonoma" />
            <span class="hud-orbit"></span>
          </div>
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


def render_ticker(items: list[str]) -> None:
    joined = "  ·  ".join(f"<span>{item}</span>" for item in items)
    st.markdown(
        f"""
        <div class="hud-ticker">
          <div class="hud-ticker-track">{joined}  ·  {joined}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rate_bar(rate: float, target: float = 95.0, label: str = "Automation Rate") -> None:
    pct = max(0.0, min(100.0, rate))
    st.markdown(
        f"""
        <div class="rate-bar-wrap">
          <div class="rate-bar-label">
            <span>{label}</span>
            <span class="val">{pct:.1f}% / {target:.0f}% target</span>
          </div>
          <div class="rate-bar-track">
            <div class="rate-bar-fill" style="width: {pct:.2f}%;"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
