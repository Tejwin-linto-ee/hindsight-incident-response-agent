import time
import streamlit as st

from app.telemetry_manager import TelemetryManager
from app.failure_predictor import FailurePredictor
from app.auth import SecurityManager


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hindsight · Incident Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM  — WORLD-CLASS CSS
# ============================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/*
  ╔══════════════════════════════════════════════════════════╗
  ║  HINDSIGHT  ·  DESIGN SYSTEM  ·  WARM MIDNIGHT PALETTE  ║
  ║  Primary:   Warm Teal    #14B8A6 → #0D9488              ║
  ║  Accent:    Amber Gold   #F59E0B → #D97706              ║
  ║  Surface:   Charcoal     #111318 → #0D1117              ║
  ║  Danger:    Rose         #FB7185 → #F43F5E              ║
  ║  Success:   Sage Green   #34D399 → #10B981              ║
  ╚══════════════════════════════════════════════════════════╝
*/

/* ─── CSS CUSTOM PROPERTIES ─────────────────────────── */
:root {
    --primary:        #14B8A6;
    --primary-dark:   #0D9488;
    --primary-light:  #5EEAD4;
    --primary-glow:   rgba(20, 184, 166, 0.25);

    --accent:         #F59E0B;
    --accent-dark:    #D97706;
    --accent-light:   #FCD34D;
    --accent-glow:    rgba(245, 158, 11, 0.22);

    --success:        #34D399;
    --success-dark:   #10B981;
    --success-glow:   rgba(52, 211, 153, 0.22);

    --danger:         #FB7185;
    --danger-dark:    #F43F5E;
    --danger-glow:    rgba(251, 113, 133, 0.22);

    --warning:        #FCD34D;
    --warning-dark:   #F59E0B;
    --warning-glow:   rgba(252, 211, 77, 0.2);

    --bg-base:        #0C1017;
    --bg-surface:     #131923;
    --bg-elevated:    #1A2332;
    --bg-overlay:     #1F2D3D;

    --border-subtle:  rgba(255, 255, 255, 0.055);
    --border-muted:   rgba(255, 255, 255, 0.09);
    --border-visible: rgba(255, 255, 255, 0.14);

    --text-primary:   #EFF6FF;
    --text-secondary: #94A3B8;
    --text-muted:     #4E6178;
    --text-disabled:  #334155;
}

/* ─── RESET & BASE ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    color: var(--text-primary) !important;
}

h1,h2,h3,h4,h5,h6,[class*="title"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--text-primary) !important;
}

/* ─── CANVAS BACKGROUND ─────────────────────────────── */
.stApp {
    background: var(--bg-base) !important;
    background-image:
        radial-gradient(ellipse 1100px 650px at 8% 4%,  rgba(20,184,166,0.09)  0%, transparent 65%),
        radial-gradient(ellipse 800px 500px  at 92% 8%,  rgba(245,158,11,0.07)  0%, transparent 60%),
        radial-gradient(ellipse 600px 400px  at 55% 92%, rgba(20,184,166,0.05)  0%, transparent 60%),
        radial-gradient(ellipse 500px 350px  at 85% 55%, rgba(251,113,133,0.04)  0%, transparent 55%) !important;
    min-height: 100vh;
}

/* ─── KEYFRAMES ─────────────────────────────────────── */
@keyframes borderGlow {
    0%   { border-color: rgba(20,184,166,0.35);  box-shadow: 0 0 20px rgba(20,184,166,0.1);  }
    50%  { border-color: rgba(245,158,11,0.3);   box-shadow: 0 0 20px rgba(245,158,11,0.08); }
    100% { border-color: rgba(20,184,166,0.35);  box-shadow: 0 0 20px rgba(20,184,166,0.1);  }
}

@keyframes livePulse {
    0%, 100% { opacity: 1; transform: scale(1);    box-shadow: 0 0 0 0 rgba(52,211,153,0.65); }
    50%       { opacity: 0.8; transform: scale(1.2); box-shadow: 0 0 0 5px rgba(52,211,153,0); }
}

@keyframes criticalPulse {
    0%, 100% { box-shadow: 0 0 0 0   rgba(251,113,133,0.5); }
    50%       { box-shadow: 0 0 0 8px rgba(251,113,133,0);   }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ─── SIDEBAR ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0F18 0%, #0D1520 60%, #0C1320 100%) !important;
    border-right: 1px solid rgba(20,184,166,0.1) !important;
    width: 280px !important;
}

section[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

section[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 1rem 0 !important;
}

/* ─── MAIN CONTENT ──────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1600px !important;
    animation: slideUp 0.4s ease-out;
}

/* ─── BUTTONS ───────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.22s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0D9488 0%, #14B8A6 50%, #0D9488 100%) !important;
    color: #ECFDF5 !important;
    border: 1px solid rgba(20,184,166,0.45) !important;
    box-shadow: 0 4px 20px rgba(20,184,166,0.3), inset 0 1px 0 rgba(255,255,255,0.18) !important;
    padding: 0.6rem 1.5rem !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 32px rgba(20,184,166,0.45), inset 0 1px 0 rgba(255,255,255,0.25) !important;
    border-color: rgba(94,234,212,0.55) !important;
    background: linear-gradient(135deg, #14B8A6 0%, #0FCCB8 50%, #0D9488 100%) !important;
}

.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

.stButton > button:not([kind="primary"]) {
    background: rgba(19,25,35,0.9) !important;
    color: #94A3B8 !important;
    border: 1px solid var(--border-muted) !important;
    backdrop-filter: blur(8px) !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: rgba(26,35,50,0.95) !important;
    color: var(--text-primary) !important;
    border-color: rgba(20,184,166,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ─── SELECTBOX ─────────────────────────────────────── */
div[data-baseweb="select"] > div {
    background: rgba(13,21,32,0.95) !important;
    border: 1px solid var(--border-muted) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: rgba(20,184,166,0.4) !important;
    box-shadow: 0 4px 16px rgba(20,184,166,0.1) !important;
}

/* ─── TEXTAREA ──────────────────────────────────────── */
.stTextArea textarea {
    background: rgba(10,15,25,0.97) !important;
    border: 1px solid var(--border-muted) !important;
    border-radius: 12px !important;
    color: #DDE4EF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.45) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    resize: none !important;
}

.stTextArea textarea:focus {
    border-color: rgba(20,184,166,0.6) !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.12), inset 0 2px 8px rgba(0,0,0,0.45) !important;
    outline: none !important;
}

/* ─── RADIO ─────────────────────────────────────────── */
.stRadio [data-testid="stMarkdownContainer"] { color: #CBD5E1 !important; }
.stRadio label { color: #DDE4EF !important; }

/* ─── EXPANDERS ─────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: rgba(13,21,32,0.75) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
    backdrop-filter: blur(12px) !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease !important;
}

div[data-testid="stExpander"]:hover { border-color: rgba(20,184,166,0.18) !important; }

div[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #94A3B8 !important;
    padding: 0.85rem 1.25rem !important;
    cursor: pointer !important;
}

div[data-testid="stExpander"] summary:hover { color: var(--text-primary) !important; }

/* ─── PROGRESS BARS ─────────────────────────────────── */
div[data-testid="stProgress"] > div > div { border-radius: 6px !important; height: 6px !important; }
div[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #0D9488, #14B8A6, #5EEAD4) !important;
    border-radius: 6px !important;
    transition: width 0.4s ease !important;
}

/* ─── DIVIDER ───────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid var(--border-subtle) !important; margin: 2rem 0 !important; }

/* ─── ALERTS ────────────────────────────────────────── */
div[data-baseweb="notification"] {
    background: rgba(13,21,32,0.97) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-muted) !important;
}

/* ─── CAPTION ────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; font-size: 0.78rem !important; }

/* ─── SPINNER ───────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ─── SCROLLBAR ─────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(20,184,166,0.25); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(20,184,166,0.45); }

/* ═══════════════════════════════════════════════════════
   HINDSIGHT COMPONENT LIBRARY
   ═══════════════════════════════════════════════════════ */

/* --- Glass Panel --- */
.glass-panel {
    background: rgba(13,21,32,0.8);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
    padding: 1.5rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
    animation: slideUp 0.3s ease-out;
}

.glass-panel:hover {
    border-color: var(--border-muted);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
}

/* --- Metric Card --- */
.metric-card {
    background: linear-gradient(145deg, rgba(19,25,35,0.95) 0%, rgba(13,21,32,0.95) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.035);
    transition: transform 0.25s cubic-bezier(0.4,0,0.2,1), box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative;
    overflow: hidden;
    min-height: 105px;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent);
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 36px rgba(0,0,0,0.5);
    border-color: var(--border-muted);
}

.metric-card.normal  { border-left: 2px solid var(--success); }
.metric-card.warning { border-left: 2px solid var(--accent); box-shadow: 0 4px 24px rgba(245,158,11,0.07), 0 0 0 1px rgba(245,158,11,0.04); }
.metric-card.critical {
    border-left: 2px solid var(--danger);
    box-shadow: 0 4px 28px rgba(251,113,133,0.15), 0 0 0 1px rgba(251,113,133,0.06);
    animation: criticalPulse 2.5s ease-in-out infinite;
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.metric-badge {
    font-size: 0.62rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.18rem 0.55rem;
    border-radius: 9999px;
    display: inline-block;
}

.badge-normal   { background: rgba(52,211,153,0.12);  color: var(--success); border: 1px solid rgba(52,211,153,0.22); }
.badge-warning  { background: rgba(245,158,11,0.12);  color: var(--accent);  border: 1px solid rgba(245,158,11,0.22); }
.badge-critical { background: rgba(251,113,133,0.12); color: var(--danger);  border: 1px solid rgba(251,113,133,0.25); }

/* --- Cluster Header --- */
.cluster-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

.cluster-label {
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--primary);
    padding: 0.2rem 0.7rem;
    background: rgba(20,184,166,0.08);
    border: 1px solid rgba(20,184,166,0.18);
    border-radius: 6px;
}

.cluster-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(20,184,166,0.18), transparent);
}

/* --- Risk Hero Panel --- */
.risk-hero {
    background: linear-gradient(135deg, rgba(10,28,26,0.97) 0%, rgba(13,21,32,0.97) 100%);
    border: 1px solid rgba(20,184,166,0.28);
    border-radius: 18px;
    padding: 1.75rem 2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 48px rgba(20,184,166,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
    animation: borderGlow 5s ease infinite;
    position: relative;
    overflow: hidden;
}

.risk-hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(20,184,166,0.04) 0%, transparent 70%);
    pointer-events: none;
}

.risk-hero.critical-state {
    background: linear-gradient(135deg, rgba(30,8,14,0.97) 0%, rgba(25,10,12,0.97) 40%, rgba(13,21,32,0.97) 100%);
    border-color: rgba(251,113,133,0.38);
    box-shadow: 0 8px 48px rgba(251,113,133,0.12), inset 0 1px 0 rgba(255,255,255,0.04);
    animation: criticalPulse 3s ease-in-out infinite;
}

/* --- Probability Bars --- */
.prob-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.6rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    transition: background 0.2s ease;
}

.prob-row:hover { background: rgba(255,255,255,0.025); }
.prob-row.is-top { background: rgba(20,184,166,0.07); border: 1px solid rgba(20,184,166,0.14); }

.prob-name { font-size: 0.83rem; font-weight: 500; color: #94A3B8; min-width: 200px; flex-shrink: 0; }
.prob-name.top-name { color: var(--primary-light); font-weight: 700; }

.prob-bar-wrap { flex: 1; height: 5px; background: rgba(255,255,255,0.05); border-radius: 9999px; overflow: hidden; }

.prob-bar-fill { height: 100%; border-radius: 9999px; background: linear-gradient(90deg, rgba(20,184,166,0.4), rgba(94,234,212,0.5)); transition: width 0.5s ease; }
.prob-bar-fill.top-fill { background: linear-gradient(90deg, #0D9488, #14B8A6, #5EEAD4); }

.prob-pct { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--text-muted); min-width: 48px; text-align: right; }
.prob-pct.top-pct { color: var(--primary-light); font-weight: 700; }

/* --- Indicator Chips --- */
.ind-chip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(13,21,32,0.85);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s ease;
}

.ind-chip:hover { border-color: var(--border-muted); }
.ind-chip.crit-chip { border-color: rgba(251,113,133,0.2); background: rgba(251,113,133,0.04); }
.ind-chip.warn-chip { border-color: rgba(245,158,11,0.2);  background: rgba(245,158,11,0.04);  }

.ind-name { font-size: 0.82rem; font-weight: 600; color: #DDE4EF; }
.ind-val  { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--text-secondary); margin: 0 0.75rem; }
.ind-badge { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; padding: 0.15rem 0.5rem; border-radius: 5px; letter-spacing: 0.06em; }
.ind-badge.crit-b { background: rgba(251,113,133,0.18); color: var(--danger); }
.ind-badge.warn-b { background: rgba(245,158,11,0.18);  color: var(--accent); }

/* --- Eyebrow / Section Labels --- */
.eyebrow {
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.3rem;
}

.eyebrow::before {
    content: '';
    display: inline-block;
    width: 14px; height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    border-radius: 2px;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.025em;
    line-height: 1.25;
    margin-bottom: 0.35rem;
}

.section-desc {
    font-size: 0.87rem;
    color: var(--text-muted);
    line-height: 1.55;
    margin-bottom: 1.25rem;
}

/* --- Status Pills --- */
.status-pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.85rem; border-radius: 9999px;
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em;
}

.pill-live    { background: rgba(52,211,153,0.1);  border: 1px solid rgba(52,211,153,0.28); color: var(--success); }
.pill-standby { background: rgba(78,97,120,0.12);  border: 1px solid rgba(78,97,120,0.22);  color: var(--text-secondary); }

.live-dot    { width:7px; height:7px; border-radius:50%; background:var(--success); box-shadow:0 0 8px var(--success); animation:livePulse 1.8s ease-in-out infinite; display:inline-block; }
.standby-dot { width:7px; height:7px; border-radius:50%; background:var(--text-muted); display:inline-block; }

/* --- Severity Badges --- */
.sev-p1 { background: rgba(251,113,133,0.12); color: var(--danger);       border: 1px solid rgba(251,113,133,0.28); padding: 0.25rem 0.75rem; border-radius: 7px; font-weight: 800; font-size: 0.85rem; }
.sev-p2 { background: rgba(245,158,11,0.12);  color: var(--accent);       border: 1px solid rgba(245,158,11,0.28);  padding: 0.25rem 0.75rem; border-radius: 7px; font-weight: 800; font-size: 0.85rem; }
.sev-p3 { background: rgba(252,211,77,0.12);  color: var(--warning);      border: 1px solid rgba(252,211,77,0.25);  padding: 0.25rem 0.75rem; border-radius: 7px; font-weight: 800; font-size: 0.85rem; }
.sev-p4 { background: rgba(78,97,120,0.12);   color: var(--text-secondary); border: 1px solid rgba(78,97,120,0.22);  padding: 0.25rem 0.75rem; border-radius: 7px; font-weight: 800; font-size: 0.85rem; }

/* --- RCA Card --- */
.rca-card {
    background: linear-gradient(145deg, rgba(19,25,35,0.95), rgba(13,21,32,0.95));
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--primary);
    border-radius: 12px;
    padding: 1.2rem 1.35rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: border-color 0.2s ease;
}

.rca-card:hover { border-left-color: var(--accent); }

/* --- Action Tier Card --- */
.action-tier {
    background: linear-gradient(145deg, rgba(17,22,32,0.95), rgba(13,21,32,0.95));
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.2rem;
    height: 100%;
    min-height: 200px;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.action-tier-header {
    font-size: 0.82rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.07em; margin-bottom: 0.9rem; padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border-subtle);
}

.action-item {
    display: flex; gap: 0.6rem; font-size: 0.84rem; color: #94A3B8;
    margin-bottom: 0.55rem; line-height: 1.45; padding: 0.35rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.025);
}

.action-num {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700;
    color: var(--primary);
    background: rgba(20,184,166,0.1);
    border-radius: 5px; padding: 0.15rem 0.4rem;
    min-width: 24px; text-align: center; flex-shrink: 0; margin-top: 0.1rem;
}

/* --- History Card --- */
.history-card {
    background: rgba(13,21,32,0.85); border: 1px solid var(--border-subtle);
    border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.6rem;
    backdrop-filter: blur(16px);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.history-card:hover { border-color: rgba(20,184,166,0.2); transform: translateX(3px); }

/* --- Review Panel --- */
.review-panel {
    background: linear-gradient(145deg, rgba(10,22,20,0.95), rgba(13,21,32,0.95));
    border: 1px solid rgba(20,184,166,0.14);
    border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

/* --- Brand Logo --- */
.brand-logo {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, #14B8A6 0%, #5EEAD4 45%, #F59E0B 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -0.02em;
}

/* --- Summary Quote --- */
.summary-quote {
    background: rgba(10,18,28,0.85);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid rgba(20,184,166,0.5);
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    font-size: 0.9rem; color: #94A3B8; line-height: 1.65;
    backdrop-filter: blur(10px);
}

/* --- Confidence Bar --- */
.conf-bar-wrap {
    height: 4px; background: rgba(255,255,255,0.05);
    border-radius: 9999px; overflow: hidden; margin-top: 0.35rem;
}
.conf-bar-fill {
    height: 100%; border-radius: 9999px;
    background: linear-gradient(90deg, #0D9488, #14B8A6);
}

/* --- Empty State --- */
.empty-state {
    text-align: center; padding: 3rem 2rem; color: var(--text-muted);
    background: rgba(13,21,32,0.6);
    border: 1px dashed rgba(255,255,255,0.05); border-radius: 14px;
}
.empty-state-icon { font-size: 2.5rem; margin-bottom: 0.75rem; display: block; opacity: 0.45; }

/* --- Alert overrides --- */
.stAlert, [data-testid="stAlert"] {
    background: rgba(13,21,32,0.95) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-muted) !important;
}
.stSuccess { border-left: 3px solid var(--success) !important; }
.stWarning { border-left: 3px solid var(--accent)  !important; }
.stError   { border-left: 3px solid var(--danger)  !important; }
.stInfo    { border-left: 3px solid var(--primary)  !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

for key, default in [
    ("authenticated", False),
    ("user_info", None),
    ("active_view", "operations"),  # "operations" or "admin_portal"
    ("telemetry_manager", None),
    ("telemetry", None),
    ("simulation_running", False),
    ("simulation_mode", "healthy"),
    ("prediction", None),
    ("investigation_result", None),
    ("sre_copilot_messages", []),
    ("webhook_url", ""),
    ("chaos_active", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.telemetry_manager is None:
    st.session_state.telemetry_manager = TelemetryManager()


# ============================================================
# LOAD PREDICTOR
# ============================================================

try:
    predictor = FailurePredictor()
    predictor_available = True
except Exception:
    predictor = None
    predictor_available = False


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

METRIC_THRESHOLDS = {
    "cpu_percent":          {"warning": 75, "critical": 90},
    "memory_percent":       {"warning": 75, "critical": 90},
    "disk_percent":         {"warning": 70, "critical": 88},
    "db_connections":       {"warning": 70, "critical": 88},
    "db_pool_usage":        {"warning": 70, "critical": 88},
    "api_latency_ms":       {"warning": 400, "critical": 900},
    "error_rate":           {"warning": 2.5, "critical": 7.0},
    "request_rate":         {"warning": 1400, "critical": 1800},
    "queue_depth":          {"warning": 80, "critical": 150},
    "network_latency_ms":   {"warning": 100, "critical": 300},
    "traffic_growth_percent": {"warning": 25, "critical": 50},
}


def metric_status(key: str, val: float) -> str:
    t = METRIC_THRESHOLDS.get(key, {})
    if val >= t.get("critical", float("inf")):
        return "critical"
    if val >= t.get("warning", float("inf")):
        return "warning"
    return "normal"


def metric_card_html(icon: str, label: str, value_str: str, key: str, val: float) -> str:
    st_class = metric_status(key, val)
    badge_class = f"badge-{st_class}"
    badge_text = st_class.upper()
    return f"""
    <div class="metric-card {st_class}">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value_str}</div>
        <div class="metric-badge {badge_class}">{badge_text}</div>
    </div>
    """


def sev_pill(sev: str) -> str:
    cls = f"sev-{sev.lower()}" if sev.lower() in ("p1","p2","p3","p4") else "sev-p4"
    return f'<span class="{cls}">🚨 {sev.upper()}</span>'


# ============================================================
# AUTHENTICATION GATE
# ============================================================

if not st.session_state.authenticated:
    st.markdown("""<div style="max-width:480px; margin:2.5rem auto 1.5rem auto; text-align:center;">
<div style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:800; background:linear-gradient(135deg,#5EEAD4 0%,#14B8A6 60%,#0D9488 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-0.03em;">
⬡ HINDSIGHT SECURE ACCESS
</div>
<p style="color:#94A3B8; font-size:0.88rem; margin-top:0.4rem;">
Enterprise Incident Intelligence & Access Control
</p>
</div>""", unsafe_allow_html=True)

    col_l, col_center, col_r = st.columns([1, 1.5, 1])
    with col_center:
        st.markdown("""<div style="background:linear-gradient(145deg,rgba(19,25,35,0.95),rgba(15,20,29,0.95)); border:1px solid rgba(255,255,255,0.09); border-radius:16px; padding:1.75rem; backdrop-filter:blur(20px); box-shadow:0 12px 40px rgba(0,0,0,0.5);">
<div style="font-size:0.8rem; font-weight:700; color:#14B8A6; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;">
<span>🔒</span> Access Gate
</div>""", unsafe_allow_html=True)

        tab_auth, tab_req = st.tabs(["🔑 Sign In", "📝 Request Access"])

        with tab_auth:
            with st.form("login_form"):
                username_input = st.text_input("Operator Username", placeholder="e.g. admin", key="login_user")
                password_input = st.text_input("Password", type="password", placeholder="••••••••••••••••", key="login_pw")
                submit_login = st.form_submit_button("🚀 Authenticate & Access", use_container_width=True)

                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    else:
                        user, msg = SecurityManager.authenticate(username_input, password_input)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_info = user
                            st.success(f"Access granted: {user['username']} ({user['role']})")
                            st.rerun()
                        else:
                            st.error(f"Access Denied: {msg}")

        with tab_req:
            st.markdown("<p style='font-size:0.8rem; color:#94A3B8; margin-bottom:0.75rem;'>Submit your credentials for Administrator approval before access is granted.</p>", unsafe_allow_html=True)
            with st.form("req_form"):
                req_user = st.text_input("Desired Username", placeholder="e.g. jdoe_sre", key="req_user")
                req_role = st.selectbox("Requested Role", ["SRE Engineer", "Incident Commander", "Platform Operations", "Security Specialist"], key="req_role")
                req_pw = st.text_input("Create Password", type="password", placeholder="Min 8 characters", key="req_pw")
                req_reason = st.text_input("Business Reason / Team", placeholder="e.g. Payment Gateway on-call team", key="req_reason")
                submit_req = st.form_submit_button("📨 Submit Access Request", use_container_width=True)

                if submit_req:
                    if not req_user or not req_pw:
                        st.error("Username and password cannot be empty.")
                    elif len(req_pw) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        ok, rmsg = SecurityManager.request_access(req_user, req_pw, req_role, req_reason)
                        if ok:
                            st.success(f"✅ {rmsg}")
                        else:
                            st.error(f"❌ {rmsg}")

        st.markdown("""<div style="margin-top:1.25rem; padding-top:0.9rem; border-top:1px solid rgba(255,255,255,0.06); font-size:0.72rem; color:#64748B; text-align:center; line-height:1.4;">
🛡️ <b>Strict RBAC & Audit Enforcement:</b> All logins and access requests are recorded in security trails.<br>
🔐 Salted Bcrypt Encryption · Cryptographic Tokenized Sessions
</div>
</div>""", unsafe_allow_html=True)

    st.stop()  # Stop execution until authenticated

with st.sidebar:
    user_info = st.session_state.get("user_info") or {"username": "admin", "role": "Lead SRE"}
    st.markdown(f"""<div style="padding:1.25rem 1.25rem 0.5rem 1.25rem;">
<div class="brand-logo">⬡ Hindsight</div>
<div style="font-size:0.72rem; color:#475569; font-weight:500; margin-top:0.15rem; letter-spacing:0.06em; text-transform:uppercase;">Incident Intelligence Platform</div>
<div style="margin-top:0.9rem; background:rgba(20,184,166,0.08); border:1px solid rgba(20,184,166,0.2); border-radius:8px; padding:0.6rem 0.75rem; display:flex; align-items:center; justify-content:space-between;">
<div>
<div style="font-size:0.78rem; font-weight:700; color:#5EEAD4;">👤 {user_info.get('username')}</div>
<div style="font-size:0.65rem; color:#94A3B8;">{user_info.get('role')}</div>
</div>
<span style="font-size:0.65rem; background:rgba(34,197,94,0.15); color:#4ADE80; padding:0.15rem 0.4rem; border-radius:4px; font-weight:700;">ACTIVE</span>
</div>
</div>""", unsafe_allow_html=True)

    is_admin = bool(user_info.get("is_admin", False) or user_info.get("username") == "admin")

    col_btn1, col_btn2 = st.columns([1, 1]) if is_admin else (st.container(), None)
    
    if is_admin:
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("📡 Ops Hub", use_container_width=True, type="primary" if st.session_state.active_view == "operations" else "secondary"):
                st.session_state.active_view = "operations"
                st.rerun()
        with c_b:
            if st.button("🛡️ Admin Portal", use_container_width=True, type="primary" if st.session_state.active_view == "admin_portal" else "secondary"):
                st.session_state.active_view = "admin_portal"
                st.rerun()

    if st.button("🔒 Sign Out", use_container_width=True, key="btn_logout"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.investigation_result = None
        st.rerun()

    st.divider()

    st.markdown("""
    <div style="padding:0 1.25rem;">
        <div style="font-size:0.65rem; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.75rem;">Intelligence Pipeline</div>
    </div>
    """, unsafe_allow_html=True)

    pipeline = [
        ("📡", "Live Telemetry",     "Streaming 11 system metrics"),
        ("🔮", "Failure Prediction", "Calibrated Random Forest (400 trees)"),
        ("🧠", "Hindsight Recall",   "Vector memory retrieval"),
        ("🤖", "Kimi K2",             "Groq · Moonshot AI · 1T MoE"),
        ("🔍", "Root Cause Analysis","AI-generated structured RCA"),
        ("👨‍🔧","Technician Review",  "Human confirmation loop"),
        ("📚", "Continuous Learning","Hindsight knowledge persistence"),
    ]

    for i, (icon, title, sub) in enumerate(pipeline):
        connector = "" if i == len(pipeline) - 1 else """
        <div style="display:flex; padding:0 1.25rem;">
            <div style="width:1px; background:linear-gradient(180deg,rgba(99,102,241,0.3),rgba(99,102,241,0.05)); height:14px; margin-left:17px;"></div>
        </div>"""
        st.markdown(f"""
        <div style="padding:0 1.25rem;">
            <div style="display:flex; align-items:center; gap:0.65rem; background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.1); border-radius:9px; padding:0.5rem 0.7rem;">
                <span style="font-size:1rem; flex-shrink:0;">{icon}</span>
                <div>
                    <div style="font-size:0.8rem; font-weight:700; color:#E2E8F0;">{title}</div>
                    <div style="font-size:0.67rem; color:#475569; margin-top:0.05rem;">{sub}</div>
                </div>
            </div>
        </div>
        {connector}
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="padding:0 1.25rem;">
        <div style="font-size:0.65rem; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.65rem;">Monitored Failure Classes</div>
        <div style="display:flex; flex-direction:column; gap:0.3rem;">
    """, unsafe_allow_html=True)

    failure_classes = [
        ("🔴","Database Pool Exhaustion"),
        ("🔴","CPU Saturation"),
        ("🔴","Memory Exhaustion"),
        ("🔴","API Availability Degradation"),
        ("🔴","Disk Storage Exhaustion"),
        ("🔴","Network Congestion"),
        ("🟢","Healthy Baseline"),
    ]

    for dot, fc in failure_classes:
        st.markdown(f"""
        <div style="font-size:0.78rem; color:#94A3B8; display:flex; align-items:center; gap:0.5rem; padding:0.25rem 0.5rem; border-radius:6px; transition:background 0.2s;">
            <span style="font-size:0.55rem;">{dot}</span> {fc}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="padding:0 1.25rem 1.25rem 1.25rem;">
        <div style="font-size:0.65rem; font-weight:800; color:#475569; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.5rem;">System Status</div>
        <div style="display:flex; flex-direction:column; gap:0.35rem; font-size:0.75rem;">
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#64748B;">Memory Store</span>
                <span style="color:#34D399; font-weight:600;">● Hindsight</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#64748B;">Reasoning Engine</span>
                <span style="color:#34D399; font-weight:600;">● Groq</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#64748B;">Predictor Model</span>
                <span style="color:{'#34D399' if predictor_available else '#F87171'}; font-weight:600;">{'● Loaded' if predictor_available else '✕ Error'}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# ADMIN GOVERNANCE & ACCESS CONTROL PORTAL
# ============================================================

current_user = st.session_state.get("user_info", {})
is_admin_user = bool(current_user.get("is_admin", False) or current_user.get("username") == "admin")

if st.session_state.active_view == "admin_portal" and is_admin_user:
    st.markdown("""<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.75rem; gap:1rem; flex-wrap:wrap;">
<div>
<div class="eyebrow">Enterprise Security Governance</div>
<h1 class="section-title" style="font-size:2.1rem; margin-bottom:0.4rem;">
🛡️ SRE Access & User Governance Portal
</h1>
<p class="section-desc" style="max-width:780px; font-size:0.92rem;">
Review pending access requests, confirm or revoke operator authorizations, assign RBAC privileges, and inspect immutable security audit trails.
</p>
</div>
<div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.5rem;">
<span class="status-pill pill-live" style="background:rgba(20,184,166,0.15); color:#5EEAD4; border-color:rgba(20,184,166,0.3);"><span class="live-dot" style="background:#5EEAD4;"></span>ADMIN PRIVILEGES ACTIVE</span>
<div style="font-size:0.7rem; color:#475569; font-family:'JetBrains Mono',monospace;">Root Security Zone</div>
</div>
</div>""", unsafe_allow_html=True)

    tab_pending, tab_directory, tab_incidents, tab_audit = st.tabs([
        "⏳ Pending Approvals", 
        "👥 Operator Directory", 
        "🗄️ Stored Issues Database", 
        "📜 Security Audit Trails"
    ])

    # 1. PENDING APPROVALS
    with tab_pending:
        all_users = SecurityManager.list_users()
        pending_users = [u for u in all_users if u.get("status") == "PENDING"]

        if not pending_users:
            st.markdown("""<div style="background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.2); border-radius:12px; padding:1.5rem; text-align:center; color:#4ADE80; font-weight:600; margin:1rem 0;">
✅ No pending access requests. All operator accounts are confirmed.
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='font-size:0.85rem; color:#F59E0B; font-weight:700; margin-bottom:1rem;'>🔔 {len(pending_users)} Access Request(s) Awaiting Administrator Confirmation:</div>", unsafe_allow_html=True)
            for pu in pending_users:
                u_name = pu.get("username")
                u_role = pu.get("role")
                u_reason = pu.get("reason", "No reason specified")
                u_time = pu.get("created_at", "")[:19].replace("T", " ")

                with st.expander(f"⏳ Access Request: {u_name}  ·  Role: {u_role}  ·  Requested at: {u_time}", expanded=True):
                    pc1, pc2, pc3 = st.columns([2.5, 1, 1], gap="medium")
                    with pc1:
                        st.markdown(f"**Operator ID:** `{u_name}`")
                        st.markdown(f"**Requested Role:** `{u_role}`")
                        st.markdown(f"**Justification / Team:** *\"{u_reason}\"*")
                        st.markdown(f"**Submission Timestamp:** `{u_time}` UTC")
                    with pc2:
                        st.write("")
                        if st.button(f"✅ Approve Access", key=f"appr_{u_name}", use_container_width=True, type="primary"):
                            SecurityManager.approve_user(u_name, current_user.get("username", "admin"))
                            st.success(f"Confirmed! User '{u_name}' is now authorized to access operations.")
                            time.sleep(0.5)
                            st.rerun()
                    with pc3:
                        st.write("")
                        if st.button(f"🚫 Decline Request", key=f"rej_{u_name}", use_container_width=True):
                            SecurityManager.reject_user(u_name, current_user.get("username", "admin"))
                            st.warning(f"Request for '{u_name}' was declined.")
                            time.sleep(0.5)
                            st.rerun()

    # 2. OPERATOR DIRECTORY & ROLE MANAGEMENT
    with tab_directory:
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#E2E8F0; margin-bottom:0.75rem;'>Active Operator Accounts & Role Governance</div>", unsafe_allow_html=True)
        all_users = SecurityManager.list_users()

        for u in all_users:
            u_name = u.get("username")
            u_role = u.get("role", "SRE Engineer")
            u_status = u.get("status", "APPROVED")
            u_is_admin = u.get("is_admin", False) or u_name == "admin"
            u_last_login = u.get("last_login") or "Never"
            if u_last_login != "Never":
                u_last_login = u_last_login[:19].replace("T", " ") + " UTC"

            badge_color = "#34D399" if u_status == "APPROVED" else ("#F59E0B" if u_status == "PENDING" else "#FB7185")

            with st.expander(f"👤 {u_name}  ·  {u_role}  ·  [{u_status}]"):
                c_info, c_action = st.columns([2, 1.2], gap="medium")
                with c_info:
                    st.markdown(f"**Username:** `{u_name}`")
                    st.markdown(f"**Role:** `{u_role}` &nbsp;|&nbsp; **Admin Privileges:** `{'Yes' if u_is_admin else 'No'}`")
                    st.markdown(f"**Account Status:** <span style='color:{badge_color}; font-weight:700;'>● {u_status}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Last Sign In:** `{u_last_login}`")
                    st.markdown(f"**Created:** `{u.get('created_at', '')[:19].replace('T', ' ')} UTC`")

                with c_action:
                    st.markdown("<div style='font-size:0.75rem; color:#64748B; font-weight:700; margin-bottom:0.4rem;'>OPERATOR ACTIONS</div>", unsafe_allow_html=True)
                    if u_name == "admin":
                        st.info("🔒 Root Administrator account cannot be modified or deleted.")
                    else:
                        new_r = st.selectbox("Update Role", ["SRE Engineer", "Incident Commander", "Platform Operations", "Security Specialist"], index=["SRE Engineer", "Incident Commander", "Platform Operations", "Security Specialist"].index(u_role) if u_role in ["SRE Engineer", "Incident Commander", "Platform Operations", "Security Specialist"] else 0, key=f"role_sel_{u_name}")
                        grant_adm = st.checkbox("Grant Admin Portal Access", value=u_is_admin, key=f"adm_chk_{u_name}")
                        
                        col_up, col_del = st.columns(2)
                        with col_up:
                            if st.button("💾 Save", key=f"save_{u_name}", use_container_width=True):
                                SecurityManager.update_user_role(u_name, new_r, grant_adm, current_user.get("username", "admin"))
                                st.success("Updated!")
                                time.sleep(0.5)
                                st.rerun()
                        with col_del:
                            if st.button("🗑️ Remove", key=f"del_{u_name}", use_container_width=True):
                                SecurityManager.delete_user(u_name, current_user.get("username", "admin"))
                                st.warning(f"Deleted user '{u_name}'")
                                time.sleep(0.5)
                                st.rerun()

    # 3. STORED ISSUES & INCIDENT DATABASE MANAGEMENT
    with tab_incidents:
        from app.incident_history import IncidentHistory
        ih = IncidentHistory()
        records = ih.get_all_incidents()

        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;'><span style='font-size:0.9rem; font-weight:700; color:#E2E8F0;'>Total Stored Incidents: {len(records)}</span></div>", unsafe_allow_html=True)

        # Danger zone: Purge all
        if records:
            with st.expander("⚠️ Danger Zone: Bulk Database Purge"):
                st.warning("This will permanently remove all stored incident postmortems, analysis records, and resolution history from the local database.")
                confirm_purge = st.checkbox("I confirm I want to permanently delete all stored incidents.", key="chk_confirm_purge")
                if st.button("🗑️ Purge All Stored Incidents", type="primary" if confirm_purge else "secondary", disabled=not confirm_purge, key="btn_purge_all"):
                    purged_count = ih.clear_all_incidents()
                    SecurityManager.log_event(
                        event_type="INCIDENTS_PURGED_ALL",
                        actor=current_user.get("username", "admin"),
                        details=f"Permanently purged all {purged_count} stored incident records",
                        status="SUCCESS"
                    )
                    st.success(f"Purged {purged_count} incident records.")
                    time.sleep(0.6)
                    st.rerun()

            st.divider()

            # Individual incident management
            st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#94A3B8; margin-bottom:0.75rem;'>INDIVIDUAL INCIDENT RECORDS</div>", unsafe_allow_html=True)
            for r in records:
                r_id = r.get("incident_id", "")
                r_sev = r.get("severity", "P3")
                r_serv = r.get("service", "Unknown")
                r_ts = r.get("created_at", "")[:19].replace("T", " ")
                r_learned = r.get("learned", False)
                status_icon = "🧠 Learned" if r_learned else "⏳ Unreviewed"

                with st.expander(f"{r_sev}  ·  {r_serv}  ·  {status_icon}  ·  ID: `{r_id[:8]}...`  ·  {r_ts}"):
                    ic1, ic2 = st.columns([3, 1], gap="medium")
                    with ic1:
                        st.markdown(f"**Full Incident ID:** `{r_id}`")
                        st.markdown(f"**Service:** `{r_serv}` &nbsp;|&nbsp; **Severity:** `{r_sev}` &nbsp;|&nbsp; **Category:** {r.get('category', '—')}")
                        st.markdown(f"**Reported Issue:** {r.get('incident', '')}")
                        st.markdown(f"**Identified Root Cause:** {r.get('root_cause', '')}")
                        if r.get("resolution"):
                            st.markdown(f"**Confirmed Fix:** `{r.get('resolution')}`")
                    with ic2:
                        st.write("")
                        st.write("")
                        if st.button(f"🗑️ Delete Issue", key=f"del_inc_{r_id}", use_container_width=True):
                            deleted = ih.delete_incident(r_id)
                            if deleted:
                                SecurityManager.log_event(
                                    event_type="INCIDENT_DELETED",
                                    actor=current_user.get("username", "admin"),
                                    details=f"Deleted incident {r_id} ({r_serv} - {r_sev})",
                                    status="SUCCESS"
                                )
                                st.success(f"Deleted incident `{r_id[:8]}`")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Failed to delete incident.")
        else:
            st.info("No incident records stored in the database.")

    # 4. AUDIT TRAILS
    with tab_audit:
        st.markdown("<div style='font-size:0.85rem; font-weight:700; color:#E2E8F0; margin-bottom:0.75rem;'>Real-Time Security & Operations Audit Log (Latest 50 events)</div>", unsafe_allow_html=True)
        logs = SecurityManager.get_audit_logs(limit=50)

        if not logs:
            st.info("No security events recorded yet.")
        else:
            for l in logs:
                ts = l.get("timestamp", "")[:19].replace("T", " ")
                ev = l.get("event_type", "EVENT")
                actor = l.get("actor", "system")
                status = l.get("status", "SUCCESS")
                details = l.get("details", "")

                status_color = "#34D399" if status == "SUCCESS" else ("#F59E0B" if status == "PENDING" else "#FB7185")

                st.markdown(f"""<div style="background:rgba(15,20,30,0.7); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:0.65rem 0.9rem; margin-bottom:0.4rem; font-family:'JetBrains Mono',monospace; font-size:0.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
<div>
<span style="color:#64748B;">[{ts}]</span>
<span style="color:#5EEAD4; font-weight:700; margin-left:0.5rem;">{ev}</span>
<span style="color:#94A3B8; margin-left:0.5rem;">actor:<b>{actor}</b></span>
<span style="color:#E2E8F0; margin-left:0.75rem;">— {details}</span>
</div>
<span style="background:rgba(255,255,255,0.05); color:{status_color}; font-weight:700; padding:0.15rem 0.45rem; border-radius:4px; font-size:0.68rem;">{status}</span>
</div>""", unsafe_allow_html=True)

    st.stop()  # Stop here if in Admin Portal view


# ============================================================
# HERO HEADER
# ============================================================

live = st.session_state.simulation_running
pill_html = (
    '<span class="status-pill pill-live"><span class="live-dot"></span>LIVE STREAMING</span>'
    if live else
    '<span class="status-pill pill-standby"><span class="standby-dot"></span>STANDBY</span>'
)

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:2rem; gap:1rem; flex-wrap:wrap;">
    <div>
        <div class="eyebrow">Enterprise SRE Intelligence</div>
        <h1 class="section-title" style="font-size:2.1rem; margin-bottom:0.4rem;">
            Hindsight Incident Command Center
        </h1>
        <p class="section-desc" style="max-width:780px; font-size:0.92rem;">
            Real-time predictive incident intelligence combining live telemetry streaming, calibrated ML failure forecasting, 
            and persistent organizational memory powered by Hindsight and Kimi K2 (Moonshot AI, 1T MoE).
        </p>
    </div>
    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.5rem; flex-shrink:0;">
        {pill_html}
        <div style="font-size:0.7rem; color:#334155; font-family:'JetBrains Mono',monospace; text-align:right;">
            v2.0 · Python 3.11 · Groq · Hindsight
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# TELEMETRY SIMULATION CONTROLS
# ============================================================

st.markdown("""
<div class="eyebrow">Telemetry & Chaos Control</div>
<div class="section-title" style="font-size:1.3rem; margin-bottom:0.25rem;">📡 Live Telemetry & Chaos Fault Injector</div>
<div class="section-desc">
    Stream continuous telemetry baseline or inject automated Chaos Engineering experiments to stress-test the ML anomaly detector.
</div>
""", unsafe_allow_html=True)

from app.chaos_engine import ChaosEngine

tab_std_sim, tab_chaos_sim = st.tabs(["📡 Standard Telemetry Stream", "💥 Chaos Fault Injection Lab"])

with tab_std_sim:
    c1, c2, c3 = st.columns([2.8, 1.6, 0.9], gap="small")

    SCENARIOS = {
        "healthy":  "🟢 Healthy Baseline — All Nominal",
        "database": "🔴 Database Pool Exhaustion",
        "cpu":      "🔴 CPU Saturation > 95%",
        "memory":   "🔴 Memory Exhaustion (OOM Risk)",
        "network":  "🔴 Network Congestion & High Latency",
        "api":      "🔴 API Availability Degradation",
    }

    with c1:
        scenario = st.selectbox(
            "Scenario",
            list(SCENARIOS.keys()),
            format_func=lambda x: SCENARIOS[x],
            index=list(SCENARIOS.keys()).index(st.session_state.simulation_mode) if st.session_state.simulation_mode in SCENARIOS else 0,
            label_visibility="collapsed",
            key="std_scenario_sel",
        )

    with c2:
        start_sim = st.button("▶  Start / Restart Stream", type="primary", use_container_width=True, key="btn_start_stream")

    with c3:
        stop_sim = st.button("■  Stop", use_container_width=True, key="btn_stop_stream")

    if start_sim:
        st.session_state.simulation_mode = scenario
        st.session_state.chaos_active = None
        try:
            st.session_state.telemetry = st.session_state.telemetry_manager.start(scenario)
            st.session_state.simulation_running = True
            st.session_state.prediction = None
        except Exception as e:
            st.error(f"Unable to start simulation: {e}")

    if stop_sim:
        try:
            st.session_state.telemetry_manager.stop()
        except Exception:
            pass
        st.session_state.simulation_running = False
        st.session_state.chaos_active = None

with tab_chaos_sim:
    all_chaos = ChaosEngine.get_all_scenarios()
    ch_col1, ch_col2 = st.columns([2.5, 1.5], gap="medium")

    with ch_col1:
        selected_chaos_id = st.selectbox(
            "Chaos Experiment Scenario",
            [s.id for s in all_chaos],
            format_func=lambda sid: ChaosEngine.get_scenario(sid).name if ChaosEngine.get_scenario(sid) else sid,
            key="chaos_exp_sel",
        )
        current_chaos = ChaosEngine.get_scenario(selected_chaos_id)
        if current_chaos:
            st.caption(f"🎯 **Target Service:** `{current_chaos.target_service}` &nbsp;|&nbsp; **Expected Type:** `{current_chaos.expected_failure_type}`")
            st.markdown(f"<div style='font-size:0.8rem; color:#94A3B8; margin-bottom:0.5rem;'>{current_chaos.description}</div>", unsafe_allow_html=True)

    with ch_col2:
        st.write("")
        if st.button("💥  Inject Chaos Fault & Trigger Triage", type="primary", use_container_width=True, key="btn_inject_chaos"):
            if current_chaos:
                st.session_state.simulation_running = False
                st.session_state.chaos_active = current_chaos.id
                # Inject the peak failure step
                peak_metrics = current_chaos.steps[-1]
                st.session_state.telemetry = dict(peak_metrics)
                if predictor_available and predictor:
                    st.session_state.prediction = predictor.predict(st.session_state.telemetry)
                
                # Security audit log
                SecurityManager.log_event(
                    event_type="CHAOS_EXPERIMENT_INJECTED",
                    actor=current_user.get("username", "anonymous"),
                    details=f"Injected chaos: {current_chaos.name} on {current_chaos.target_service}",
                    status="SUCCESS"
                )
                st.success(f"⚡ Injected fault: {current_chaos.name} — Metrics pushed to ML engine!")
                st.rerun()

if st.session_state.simulation_running:
    try:
        sample = st.session_state.telemetry_manager.next_sample()
        if sample:
            st.session_state.telemetry = sample
    except Exception as e:
        st.error(f"Telemetry stream error: {e}")

telemetry = st.session_state.telemetry


# ============================================================
# TELEMETRY METRIC CARDS
# ============================================================

if telemetry:
    # Cluster 1 — Compute
    st.markdown('<div class="cluster-header"><span class="cluster-label">⚙ Compute & Resources</span><div class="cluster-line"></div></div>', unsafe_allow_html=True)
    cols = st.columns(4, gap="small")
    cards = [
        ("💻", "CPU Utilization",  f"{telemetry.get('cpu_percent',0):.1f}%",     "cpu_percent"),
        ("🧠", "Memory Usage",     f"{telemetry.get('memory_percent',0):.1f}%",  "memory_percent"),
        ("💾", "Disk Storage",     f"{telemetry.get('disk_percent',0):.1f}%",    "disk_percent"),
        ("🏊", "DB Pool Usage",    f"{telemetry.get('db_pool_usage',0):.1f}%",   "db_pool_usage"),
    ]
    for col, (icon, label, val_str, key) in zip(cols, cards):
        with col:
            st.markdown(metric_card_html(icon, label, val_str, key, telemetry.get(key,0)), unsafe_allow_html=True)

    # Cluster 2 — Service Health
    st.markdown('<div class="cluster-header"><span class="cluster-label">🏥 Service Health & Database</span><div class="cluster-line"></div></div>', unsafe_allow_html=True)
    cols = st.columns(4, gap="small")
    cards2 = [
        ("🔌", "Active DB Conns",  f"{telemetry.get('db_connections',0):.1f}%", "db_connections"),
        ("⏱️", "API Latency",       f"{telemetry.get('api_latency_ms',0):.0f}ms", "api_latency_ms"),
        ("⚠️", "HTTP Error Rate",   f"{telemetry.get('error_rate',0):.2f}%",     "error_rate"),
        ("📬", "Request Queue",    f"{telemetry.get('queue_depth',0):.0f}",      "queue_depth"),
    ]
    for col, (icon, label, val_str, key) in zip(cols, cards2):
        with col:
            st.markdown(metric_card_html(icon, label, val_str, key, telemetry.get(key,0)), unsafe_allow_html=True)

    # Cluster 3 — Traffic & Network
    st.markdown('<div class="cluster-header"><span class="cluster-label">🌐 Traffic & Network</span><div class="cluster-line"></div></div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    cards3 = [
        ("📈", "Req. Rate",         f"{telemetry.get('request_rate',0):.0f}/s",  "request_rate"),
        ("🌐", "Network Latency",   f"{telemetry.get('network_latency_ms',0):.0f}ms", "network_latency_ms"),
        ("🚀", "Traffic Growth",    f"+{telemetry.get('traffic_growth_percent',0):.1f}%", "traffic_growth_percent"),
    ]
    for col, (icon, label, val_str, key) in zip(cols, cards3):
        with col:
            st.markdown(metric_card_html(icon, label, val_str, key, telemetry.get(key,0)), unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-state-icon">📡</span>
        <div style="font-size:1rem; font-weight:700; color:#334155; margin-bottom:0.3rem;">No Telemetry Stream Active</div>
        <div style="font-size:0.85rem;">Select a scenario and click <strong>Start / Restart Stream</strong> above to begin live monitoring.</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# RUN FAILURE PREDICTION
# ============================================================

if telemetry and predictor_available and predictor:
    try:
        pred = predictor.predict(telemetry)
        st.session_state.prediction = pred
    except Exception:
        st.session_state.prediction = None

prediction = st.session_state.prediction


# ============================================================
# PREDICTIVE FAILURE INTELLIGENCE
# ============================================================

if prediction:
    st.divider()

    risk          = int(prediction.get("failure_risk", 0))
    risk_level    = str(prediction.get("risk_level", "LOW"))
    pred_failure  = str(prediction.get("predicted_failure", "No immediate failure predicted"))
    failure_type  = str(prediction.get("predicted_failure_type", "No Failure"))
    type_prob     = float(prediction.get("predicted_failure_probability", 0))
    risk_window   = str(prediction.get("risk_window", "No immediate failure window detected"))
    confidence    = float(prediction.get("prediction_confidence", 0))
    model_name    = str(prediction.get("model", "Calibrated Multiclass Random Forest"))

    is_crit       = risk >= 60
    hero_cls      = "risk-hero critical-state" if is_crit else "risk-hero"

    level_cfg = {
        "CRITICAL": ("#F87171", "#EF4444"),
        "HIGH":     ("#FB923C", "#F97316"),
        "MEDIUM":   ("#FBBF24", "#F59E0B"),
        "LOW":      ("#34D399", "#10B981"),
    }
    l_text, l_color = level_cfg.get(risk_level, ("#94A3B8","#64748B"))

    st.markdown('<div class="eyebrow">AI Forecasting Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:1.3rem; margin-bottom:1rem;">🔮 Predictive Failure Intelligence</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="{hero_cls}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1.5rem; margin-bottom:1.25rem;">
            <div style="flex:1; min-width:240px;">
                <div style="font-size:0.7rem; font-weight:800; color:{l_color}; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.4rem;">{risk_level} RISK</div>
                <div style="font-size:1.5rem; font-weight:800; color:#FFFFFF; line-height:1.2; margin-bottom:0.5rem;">{pred_failure}</div>
                <div style="font-size:0.88rem; color:#94A3B8;">Predicted type: <strong style="color:#E2E8F0;">{failure_type}</strong> &nbsp;·&nbsp; {type_prob:.1f}% probability</div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.6rem;">
                <div style="background:rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:0.75rem 1.25rem; text-align:center; min-width:120px;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:2.2rem; font-weight:800; color:{l_color}; line-height:1;">{risk}%</div>
                    <div style="font-size:0.65rem; color:#64748B; margin-top:0.15rem; text-transform:uppercase; letter-spacing:0.06em;">Failure Risk</div>
                </div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:0.75rem;">
            <div style="background:rgba(0,0,0,0.3); border-radius:9px; padding:0.7rem 0.9rem; border:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.65rem; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">⏱ Time to Failure</div>
                <div style="font-size:0.88rem; font-weight:600; color:#F1F5F9;">{prediction.get('time_to_failure', risk_window)}</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border-radius:9px; padding:0.7rem 0.9rem; border:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.65rem; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">🚨 Urgency Index</div>
                <div style="font-size:0.88rem; font-weight:700; color:{l_color};">{prediction.get('urgency_index', risk)}/100</div>
                <div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{prediction.get('urgency_index', risk)}%;"></div></div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border-radius:9px; padding:0.7rem 0.9rem; border:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.65rem; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">📈 Anomaly Score</div>
                <div style="font-size:0.88rem; font-weight:700; color:#FCD34D;">{prediction.get('anomaly_score', 0.0):.2f}σ</div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border-radius:9px; padding:0.7rem 0.9rem; border:1px solid rgba(255,255,255,0.06);">
                <div style="font-size:0.65rem; color:#475569; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">🎯 Model Confidence</div>
                <div style="font-size:0.88rem; font-weight:600; color:#34D399;">{confidence:.0f}%</div>
                <div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{confidence}%;"></div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Probabilities + Indicators split
    pcol1, pcol2 = st.columns([1.3, 1], gap="large")

    with pcol1:
        st.markdown('<div style="font-size:0.88rem; font-weight:700; color:#E2E8F0; margin-bottom:0.85rem; margin-top:0.25rem;">📊 Failure Class Probabilities</div>', unsafe_allow_html=True)
        probs = prediction.get("failure_type_probabilities", [])
        for item in probs:
            name   = item.get("display_name", item.get("failure_type","?"))
            prob   = float(item.get("probability", 0))
            is_top = (name == failure_type and prob > 3.0)
            row_cls  = "prob-row is-top" if is_top else "prob-row"
            name_cls = "prob-name top-name" if is_top else "prob-name"
            fill_cls = "prob-bar-fill top-fill" if is_top else "prob-bar-fill"
            pct_cls  = "prob-pct top-pct" if is_top else "prob-pct"
            fill_pct = max(1, min(100, int(prob)))
            st.markdown(f"""
            <div class="{row_cls}">
                <span class="{name_cls}">{name}</span>
                <div class="prob-bar-wrap"><div class="{fill_cls}" style="width:{fill_pct}%;"></div></div>
                <span class="{pct_cls}">{prob:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)

    with pcol2:
        st.markdown('<div style="font-size:0.88rem; font-weight:700; color:#E2E8F0; margin-bottom:0.85rem; margin-top:0.25rem;">⚠️ Active Risk Indicators</div>', unsafe_allow_html=True)
        evidence = prediction.get("evidence", [])
        if evidence:
            for ind in evidence:
                feat = ind.get("feature","metric")
                val  = ind.get("value","")
                sev  = ind.get("status","WARNING")
                chip_cls = "crit-chip" if sev == "CRITICAL" else "warn-chip"
                b_cls    = "crit-b"   if sev == "CRITICAL" else "warn-b"
                st.markdown(f"""
                <div class="ind-chip {chip_cls}">
                    <span class="ind-name">{feat}</span>
                    <span class="ind-val">{val}</span>
                    <span class="ind-badge {b_cls}">{sev}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.15); border-radius:10px; padding:1rem; text-align:center; color:#34D399; font-size:0.85rem; font-weight:600;">
                🟢 All metrics within nominal thresholds
            </div>
            """, unsafe_allow_html=True)

        attributions = prediction.get("feature_attributions", [])
        if attributions:
            with st.expander("🔍 Explainable AI · Telemetry Drivers Attribution", expanded=True):
                for attr in attributions:
                    feat_name = attr.get("feature", "")
                    pct = attr.get("attribution_percent", 0)
                    is_drv = attr.get("is_driver", False)
                    color = "#FB7185" if is_drv else "#14B8A6"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; padding:0.3rem 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                        <span style="font-weight:600; color:{'#F1F5F9' if is_drv else '#94A3B8'};">{'🚨 ' if is_drv else '• '}{feat_name}</span>
                        <span style="font-family:'JetBrains Mono',monospace; color:{color}; font-weight:700;">{pct}% impact</span>
                    </div>
                    """, unsafe_allow_html=True)

    # Preemptive Remediation Playbook
    preemptive = prediction.get("preemptive_remediation", [])
    if preemptive and risk >= 30:
        st.markdown("""
        <div style="background:rgba(20,184,166,0.07); border:1px solid rgba(20,184,166,0.2); border-radius:12px; padding:1rem 1.25rem; margin-top:1rem;">
            <div style="font-size:0.75rem; font-weight:800; color:#5EEAD4; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">⚡ Pre-Emptive SRE Mitigation Playbook</div>
        """, unsafe_allow_html=True)
        for i, step in enumerate(preemptive, 1):
            st.markdown(f"<div style='font-size:0.84rem; color:#E2E8F0; margin-bottom:0.35rem;'><strong>{i}.</strong> {step}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# INCIDENT INVESTIGATION
# ============================================================

st.divider()

st.markdown("""
<div class="eyebrow">AI Investigation Engine</div>
<div class="section-title" style="font-size:1.3rem; margin-bottom:0.25rem;">🔍 Incident Investigation & Root Cause Analysis</div>
<div class="section-desc">
    Describe observed symptoms. The agent retrieves matching historical incidents from Hindsight organizational memory, 
    correlates with live telemetry and ML failure predictions, and generates a full structured RCA.
</div>
""", unsafe_allow_html=True)

incident_text = st.text_area(
    "Incident Description",
    value=(
        "The Payment API is returning HTTP 503 errors. "
        "Database connections are timing out and the database connection pool is nearly full. "
        "API latency and error rate are increasing, and the request queue is growing."
    ),
    height=105,
    label_visibility="collapsed",
)

if st.button("🧠  Investigate Current System State", type="primary", use_container_width=True):
    if not incident_text.strip():
        st.warning("Please enter an incident description.")
    else:
        try:
            from app.agent import IncidentResponseAgent

            current_telemetry  = st.session_state.telemetry
            current_prediction = st.session_state.prediction

            if current_telemetry and not current_prediction and predictor_available and predictor:
                try:
                    current_prediction = predictor.predict(current_telemetry)
                    st.session_state.prediction = current_prediction
                except Exception:
                    pass

            agent = IncidentResponseAgent()

            with st.spinner("Recalling Hindsight memories · Reasoning with Kimi K2 · Generating RCA..."):
                result = agent.investigate(
                    incident=incident_text,
                    telemetry=current_telemetry,
                    prediction=current_prediction,
                )

            st.session_state.investigation_result = result
            
            # Security audit log
            SecurityManager.log_event(
                event_type="INCIDENT_INVESTIGATED",
                actor=current_user.get("username", "anonymous"),
                details=f"Investigated: {incident_text[:60]}... (Severity: {result.get('analysis', {}).get('severity', 'P3')})",
                status="SUCCESS"
            )

            try:
                agent.close()
            except Exception:
                pass

            st.success("✅ Incident investigation complete — analysis ready below.")
            st.rerun()

        except Exception as e:
            msg = str(e)
            if "OPENROUTER_API_KEY" in msg or "openrouter" in msg.lower() or "GROQ_API_KEY" in msg or "groq" in msg.lower():
                st.error("⚠️ **LLM API Unavailable** — Verify `OPENROUTER_API_KEY` in `.env` — get a free key at https://openrouter.ai/keys")
            elif "HINDSIGHT" in msg or "hindsight" in msg.lower():
                st.error("⚠️ **Hindsight Memory Unavailable** — Verify `HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL`, `HINDSIGHT_BANK_ID` in `.env`.")
            else:
                st.error(f"⚠️ **Investigation failed:** {msg}")


# ============================================================
# RCA PRESENTATION
# ============================================================

result = st.session_state.investigation_result

if result:
    st.divider()

    analysis    = result.get("analysis", result)
    incident_id = result.get("incident_id", "")

    sev      = str(analysis.get("severity", "P3")).upper()
    service  = str(analysis.get("service", "Unknown"))
    category = str(analysis.get("category", "General"))
    ai_conf  = int(analysis.get("confidence", 0))
    root_conf= int(analysis.get("root_cause_confidence", ai_conf))

    st.markdown(f"""
    <div style="background:linear-gradient(145deg,rgba(18,25,55,0.95),rgba(14,20,40,0.95)); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:1.5rem; margin-bottom:1.5rem; backdrop-filter:blur(20px); box-shadow:0 8px 32px rgba(0,0,0,0.4);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-bottom:1.25rem;">
            <div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap;">
                {sev_pill(sev)}
                <span style="background:rgba(30,41,59,0.9); color:#F1F5F9; border:1px solid rgba(255,255,255,0.08); font-weight:600; font-size:0.82rem; padding:0.25rem 0.7rem; border-radius:7px;">🏢 {service}</span>
                <span style="background:rgba(30,41,59,0.9); color:#94A3B8; border:1px solid rgba(255,255,255,0.07); font-size:0.8rem; padding:0.25rem 0.7rem; border-radius:7px;">🏷️ {category}</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span style="font-size:0.78rem; color:#64748B;">AI Confidence</span>
                <span style="background:rgba(16,185,129,0.12); color:#34D399; border:1px solid rgba(16,185,129,0.25); font-weight:800; font-size:0.82rem; padding:0.2rem 0.65rem; border-radius:6px;">{ai_conf}%</span>
            </div>
        </div>
        <div style="font-size:0.68rem; color:#334155; font-family:'JetBrains Mono',monospace;">Tracking ID: {incident_id}</div>
    </div>
    """, unsafe_allow_html=True)

    # Summary + RCA side by side
    sc1, sc2 = st.columns(2, gap="medium")

    with sc1:
        st.markdown(f"""
        <div class="glass-panel" style="padding:1.1rem 1.25rem;">
            <div style="font-size:0.68rem; font-weight:800; color:#818CF8; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">📌 Executive Summary</div>
            <div class="summary-quote">{analysis.get("incident_summary","No summary.")}</div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div class="rca-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <div style="font-size:0.68rem; font-weight:800; color:#818CF8; text-transform:uppercase; letter-spacing:0.1em;">🎯 Likely Root Cause</div>
                <div style="font-size:0.72rem; font-family:'JetBrains Mono',monospace; color:#475569;">Confidence: {root_conf}%</div>
            </div>
            <div style="font-size:0.92rem; font-weight:600; color:#F1F5F9; line-height:1.55;">
                {analysis.get("root_cause","No root cause identified.")}
            </div>
            <div class="conf-bar-wrap" style="margin-top:0.75rem;"><div class="conf-bar-fill" style="width:{root_conf}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    # Historical Evidence & Semantic Memory Recall
    structured_memories = result.get("structured_memories", [])
    historical = analysis.get("historical_evidence", [])

    if structured_memories or historical:
        count = len(structured_memories) if structured_memories else len(historical)
        with st.expander(f"🧠 Multi-Tier Historical Memory · {count} Relevant Incidents Recalled from Hindsight", expanded=True):
            if structured_memories:
                for i, sm in enumerate(structured_memories, 1):
                    rel = sm.get("relevance_score", 50.0)
                    tier = sm.get("tier", "Contextual")
                    tier_badge = sm.get("tier_badge", "LOW")
                    b_color = "#34D399" if tier_badge == "HIGH" else "#F59E0B" if tier_badge == "MODERATE" else "#94A3B8"
                    st.markdown(f"""
                    <div style="background:rgba(15,23,42,0.85); border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.75rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                            <span style="font-weight:700; color:#F1F5F9; font-size:0.85rem;">Memory #{i} · {sm.get('extracted_service', 'Service')}</span>
                            <span style="background:rgba(255,255,255,0.05); color:{b_color}; border:1px solid {b_color}44; font-size:0.72rem; font-weight:800; padding:0.15rem 0.5rem; border-radius:6px; font-family:'JetBrains Mono',monospace;">
                                {rel}% Relevance ({tier_badge})
                            </span>
                        </div>
                        <div style="font-size:0.82rem; color:#94A3B8; margin-bottom:0.4rem; white-space:pre-wrap;">{sm.get('raw_text','')[:350]}...</div>
                        <div style="font-size:0.78rem; color:#34D399; font-weight:600; background:rgba(16,185,129,0.06); border-radius:6px; padding:0.35rem 0.6rem;">
                            💡 Confirmed Past Fix: {sm.get('extracted_resolution', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                for i, ev in enumerate(historical, 1):
                    if isinstance(ev, dict):
                        st.markdown(f"**Memory {i}:** {ev.get('incident', str(ev))}")
                        if ev.get("relevance"):
                            st.caption(f"Relevance signal: {ev['relevance']}")
                    else:
                        st.markdown(f"• {ev}")

    # 3-Tier Action Plan
    st.markdown('<div style="margin-top:1.5rem; font-size:0.88rem; font-weight:700; color:#F1F5F9; margin-bottom:0.75rem;">🛠️ Structured Remediation Plan</div>', unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3, gap="medium")

    tiers = [
        (a1, "⚡ Immediate Triage",        "Contain now — stop the bleeding",           "#EF4444", analysis.get("recommended_actions",[])),
        (a2, "🔧 Short-Term Stabilization","Stabilize the service within hours",         "#F59E0B", analysis.get("short_term_actions",[])),
        (a3, "🛡️ Long-Term Prevention",    "Architectural hardening — prevent recurrence","#10B981", analysis.get("long_term_prevention",[])),
    ]

    for col, title, subtitle, color, actions in tiers:
        with col:
            st.markdown(f"""
            <div class="action-tier">
                <div class="action-tier-header" style="color:{color}; border-bottom-color:rgba(255,255,255,0.07);">
                    {title}
                    <div style="font-size:0.67rem; font-weight:500; color:#475569; text-transform:none; letter-spacing:0; margin-top:0.1rem;">{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)
            if actions:
                for i, act in enumerate(actions, 1):
                    act_str = str(act) if not isinstance(act, dict) else str(list(act.values())[0])
                    st.markdown(f"""
                    <div class="action-item">
                        <span class="action-num">{i}</span>
                        <span>{act_str[:220]}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.82rem; color:#334155;">No actions returned.</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # AI Reasoning
    with st.expander("🤖 AI Reasoning Chain & Confidence Analysis"):
        reasoning = analysis.get("reasoning_summary", analysis.get("reasoning","No reasoning."))
        uncertainty = analysis.get("uncertainty","No uncertainty reported.")
        st.markdown(f"**Model Reasoning:**\n\n{reasoning}")
        st.markdown(f"**Known Limitations:**\n\n{uncertainty}")

    # ========================================================
    # ENGINEER REVIEW
    # ========================================================

    st.markdown('<div style="margin-top:1.5rem;"></div>', unsafe_allow_html=True)
    # ========================================================
    # SRE PLATFORM COMMAND TABS
    # ========================================================

    tab_review, tab_runbook, tab_postmortem, tab_chat, tab_alerts = st.tabs([
        "👨‍🔧 Engineer Review & Learning",
        "⚡ Actionable Runbooks & CLI",
        "📑 Executive Postmortem (RCA)",
        "💬 Interactive SRE Copilot Chat",
        "📢 Real-Time Alert Dispatcher",
    ])

    # 1. ENGINEER REVIEW & CONTINUOUS LEARNING TAB
    with tab_review:
        st.markdown("""
        <div class="eyebrow">Human-in-the-Loop</div>
        <div class="section-title" style="font-size:1.1rem; margin-bottom:0.25rem;">Confirm Fix & Ingest to Hindsight</div>
        <div class="section-desc">
            Confirm the actual production fix. Your response trains Hindsight to improve future automated recommendations.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="review-panel">', unsafe_allow_html=True)

        helpful = st.radio(
            "Was the AI recommendation accurate?",
            ["✅ Helpful — Accurate diagnosis & actions", "❌ Not Helpful — Missed the root cause"],
            horizontal=True,
            key="helpful_radio",
        )

        resolution = st.text_area(
            "Confirmed Resolution",
            placeholder="Describe the actual technical fix applied in production by the on-call engineer...",
            height=90,
            label_visibility="visible",
            key="res_input_text",
        )

        if st.button("📚  Commit Resolution to Hindsight Memory", type="primary", use_container_width=True, key="btn_save_res"):
            if not resolution.strip():
                st.warning("Enter the confirmed resolution before saving.")
            elif not incident_id:
                st.error("Missing incident ID.")
            else:
                try:
                    from app.agent import IncidentResponseAgent
                    review_agent = IncidentResponseAgent()
                    with st.spinner("Persisting confirmed resolution into Hindsight organizational memory..."):
                        review_agent.record_resolution(
                            incident_id=incident_id,
                            helpful=("Helpful" in helpful),
                            resolution=resolution,
                        )
                    try:
                        review_agent.close()
                    except Exception:
                        pass
                    st.success("✅ Confirmed resolution persisted. Hindsight has learned from this incident.")
                    st.rerun()
                except Exception as e:
                    msg = str(e)
                    if "hindsight" in msg.lower() or "HINDSIGHT" in msg:
                        st.error(f"⚠️ Hindsight unavailable: {msg}")
                    else:
                        st.error(f"⚠️ Unable to save review: {msg}")

        st.markdown("</div>", unsafe_allow_html=True)

    # 2. ACTIONABLE RUNBOOKS & CLI SCRIPTS TAB
    with tab_runbook:
        from app.runbook_generator import RunbookGenerator
        runbook = result.get("runbook") or RunbookGenerator.generate_runbook(analysis, telemetry=result.get("telemetry"))

        st.markdown(f"""
        <div style="margin-bottom:1rem;">
            <div style="font-size:0.75rem; font-weight:800; color:#5EEAD4; text-transform:uppercase; letter-spacing:0.08em;">Auto-Generated Production Runbook</div>
            <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF;">Target Service: <code>{runbook.get('service', 'app')}</code> ({runbook.get('severity', 'P2')})</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🚀 Execution Sequence")
        for cmd_item in runbook.get("commands", []):
            with st.expander(f"📌 {cmd_item.get('title', 'Command')}", expanded=True):
                st.caption(cmd_item.get("description", ""))
                st.code(cmd_item.get("command", ""), language=cmd_item.get("type", "bash"))

        col_rb1, col_rb2 = st.columns(2, gap="medium")
        with col_rb1:
            st.markdown("#### 🛡️ Pre-Flight Safety Checks")
            for sc in runbook.get("safety_checks", []):
                st.markdown(f"- ⚠️ {sc}")

        with col_rb2:
            st.markdown("#### 🔍 Post-Remediation Verification")
            for vs in runbook.get("verification_steps", []):
                st.markdown(f"- ✅ {vs}")

        if runbook.get("rollback_commands"):
            with st.expander("🔄 Emergency Rollback Procedure"):
                for rb in runbook.get("rollback_commands", []):
                    st.markdown(f"**{rb.get('title', 'Rollback')}** — {rb.get('description', '')}")
                    st.code(rb.get("command", ""), language="bash")

    # 3. EXECUTIVE POSTMORTEM (RCA) EXPORTER TAB
    with tab_postmortem:
        from app.postmortem_exporter import PostmortemExporter
        inc_raw_text = result.get("incident", incident_text)
        current_telemetry = result.get("telemetry")
        current_author = user_info.get("username", "admin")

        postmortem_md = PostmortemExporter.generate_markdown(
            analysis=analysis,
            incident_text=inc_raw_text,
            telemetry=current_telemetry,
            incident_id=incident_id,
            author=f"{current_author} ({user_info.get('role', 'SRE')})",
        )
        postmortem_json = PostmortemExporter.generate_json(
            analysis=analysis,
            incident_text=inc_raw_text,
            telemetry=current_telemetry,
            incident_id=incident_id,
        )

        st.markdown("""
        <div style="margin-bottom:1rem;">
            <div style="font-size:0.75rem; font-weight:800; color:#5EEAD4; text-transform:uppercase; letter-spacing:0.08em;">Formal Incident Postmortem & Five-Whys RCA</div>
            <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF;">Export Ready Document for Jira, Confluence, and Leadership</div>
        </div>
        """, unsafe_allow_html=True)

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="📥 Download Postmortem (Markdown .md)",
                data=postmortem_md,
                file_name=f"postmortem_{incident_id or 'incident'}.md",
                mime="text/markdown",
                use_container_width=True,
                type="primary",
            )
        with d_col2:
            st.download_button(
                label="📥 Download Full Incident Data (JSON)",
                data=postmortem_json,
                file_name=f"incident_{incident_id or 'incident'}.json",
                mime="application/json",
                use_container_width=True,
            )

        with st.expander("👀 Preview Generated Postmortem Markdown", expanded=False):
            st.markdown(postmortem_md)

    # 4. INTERACTIVE SRE COPILOT CHAT TAB
    with tab_chat:
        st.markdown("""
        <div style="margin-bottom:0.75rem;">
            <div style="font-size:0.75rem; font-weight:800; color:#5EEAD4; text-transform:uppercase; letter-spacing:0.08em;">Live SRE Copilot Chat</div>
            <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF;">Ask Follow-Up Questions to Kimi K2</div>
        </div>
        """, unsafe_allow_html=True)

        from app.sre_chat import SRECopilot
        if "sre_copilot_instance" not in st.session_state:
            st.session_state.sre_copilot_instance = SRECopilot()

        copilot = st.session_state.sre_copilot_instance

        for msg in st.session_state.sre_copilot_messages:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            role_color = "#94A3B8" if msg["role"] == "user" else "#5EEAD4"
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.7); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:0.65rem 0.9rem; margin-bottom:0.5rem;">
                <div style="font-size:0.72rem; font-weight:700; color:{role_color}; margin-bottom:0.25rem;">{role_icon} {msg['role'].upper()}</div>
                <div style="font-size:0.85rem; color:#E2E8F0; white-space:pre-wrap;">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

        user_q = st.text_input("Ask Copilot about trade-offs, alternative fixes, or historical precedents...", key="copilot_q_input")
        c_ask1, c_ask2 = st.columns([4, 1])
        with c_ask2:
            if st.button("💬 Send", use_container_width=True, key="btn_send_copilot"):
                if user_q.strip():
                    st.session_state.sre_copilot_messages.append({"role": "user", "content": user_q.strip()})
                    with st.spinner("Copilot analyzing context..."):
                        reply = copilot.ask(user_q, incident_context=analysis)
                        st.session_state.sre_copilot_messages.append({"role": "assistant", "content": reply})
                    st.rerun()

    # 5. REAL-TIME ALERT DISPATCHER TAB
    with tab_alerts:
        from app.alert_dispatcher import AlertDispatcher

        st.markdown("""
        <div style="margin-bottom:0.75rem;">
            <div style="font-size:0.75rem; font-weight:800; color:#5EEAD4; text-transform:uppercase; letter-spacing:0.08em;">Real-Time Notification Dispatcher</div>
            <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF;">Send Incident Card to Slack, Teams, or PagerDuty</div>
        </div>
        """, unsafe_allow_html=True)

        wh_url = st.text_input("Webhook URL (Slack / Teams / Discord / Generic)", value=st.session_state.webhook_url, placeholder="https://hooks.slack.com/services/...", key="wh_url_input")
        st.session_state.webhook_url = wh_url

        target_platform = st.selectbox("Platform Format", ["Slack Block Kit", "Microsoft Teams MessageCard", "Generic JSON Payload"])

        if st.button("📢  Dispatch Alert Now", type="primary", use_container_width=True, key="btn_dispatch_alert"):
            if not wh_url.strip():
                st.warning("Please provide a valid webhook URL.")
            else:
                if target_platform == "Slack Block Kit":
                    payload = AlertDispatcher.format_slack_card(analysis, incident_id=incident_id)
                elif target_platform == "Microsoft Teams MessageCard":
                    payload = AlertDispatcher.format_teams_card(analysis, incident_id=incident_id)
                else:
                    payload = {"incident_id": incident_id, "analysis": analysis, "telemetry": result.get("telemetry")}

                with st.spinner("Dispatching webhook alert..."):
                    res = AlertDispatcher.dispatch(wh_url, payload)

                if res.get("success"):
                    st.success(f"✅ Alert successfully sent to {target_platform}!")
                    SecurityManager.log_event(
                        event_type="ALERT_DISPATCHED",
                        actor=user_info.get("username", "admin"),
                        details=f"Dispatched {target_platform} alert for {incident_id}",
                        status="SUCCESS"
                    )
                else:
                    st.error(f"❌ Webhook dispatch failed: {res.get('error')}")


# ============================================================
# INCIDENT LEARNING HISTORY
# ============================================================

st.divider()

st.markdown("""
<div class="eyebrow">Organizational Knowledge</div>
<div class="section-title" style="font-size:1.3rem; margin-bottom:0.25rem;">📚 Incident Learning History</div>
<div class="section-desc">
    Persistent local incident registry. Human-confirmed resolutions feed back into Hindsight for intelligent future recall.
</div>
""", unsafe_allow_html=True)

try:
    from app.incident_history import IncidentHistory
    history = IncidentHistory().get_all()
except Exception as e:
    history = []
    st.warning(f"Unable to load history: {e}")

if not history:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-state-icon">📭</span>
        <div style="font-size:1rem; font-weight:700; color:#334155; margin-bottom:0.3rem;">No Incidents Recorded Yet</div>
        <div style="font-size:0.84rem;">Run an investigation above to create the first record.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.caption(f"{len(history)} incident record(s) in local knowledge store")

    for record in reversed(history):
        rec_id    = record.get("incident_id","")
        sev       = record.get("severity","—")
        service   = record.get("service","Unknown")
        learned   = record.get("learned", False)
        ts        = record.get("created_at","")[:19].replace("T"," ")
        status_lbl= "🧠 Learned" if learned else "⏳ Awaiting Review"

        with st.expander(f"{status_lbl}  ·  {sev}  ·  {service}  ·  {ts}"):
            hc1, hc2 = st.columns(2, gap="medium")
            with hc1:
                st.markdown(f"**Incident ID:** `{rec_id}`")
                st.markdown(f"**Severity:** `{sev}` &nbsp;|&nbsp; **Category:** {record.get('category','—')}")
                st.markdown(f"**AI Confidence:** {record.get('confidence',0)}%")
                st.markdown("**Original Incident:**")
                st.write(record.get("incident",""))
            with hc2:
                st.markdown("**AI Identified Root Cause:**")
                st.write(record.get("root_cause",""))
                res = record.get("resolution")
                if res:
                    st.markdown("**Confirmed Engineer Fix:**")
                    st.success(res)
                else:
                    st.info("⏳ Awaiting human confirmation.")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.72rem; color:#1E293B; flex-wrap:wrap; gap:0.5rem; padding-bottom:1.5rem;">
    <div style="display:flex; align-items:center; gap:0.75rem;">
        <span class="brand-logo" style="font-size:0.85rem;">⬡ Hindsight</span>
        <span style="color:#1E293B;">Incident Intelligence Platform · v2.0</span>
    </div>
    <div>Human review required before applying any production mitigation.</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# AUTO-REFRESH LOOP
# ============================================================

if st.session_state.simulation_running:
    time.sleep(1)
    st.rerun()