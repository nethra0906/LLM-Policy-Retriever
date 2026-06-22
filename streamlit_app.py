"""
Policy Intelligence Platform — Streamlit UI.

Run: streamlit run streamlit_app.py
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Policy Intelligence Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS / design system ─────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ═══════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════ */
:root {
    --bg-base:        #0a0f1e;
    --bg-surface:     #111827;
    --bg-elevated:    #1a2236;
    --bg-card:        #1e2d45;

    --accent-indigo:  #4f46e5;
    --accent-cyan:    #06b6d4;
    --accent-purple:  #7c3aed;
    --accent-glow:    rgba(79, 70, 229, 0.35);

    --text-primary:   #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted:     #475569;

    --border-subtle:  rgba(255,255,255,0.07);
    --border-active:  rgba(79,70,229,0.6);

    --conf-high:      #10b981;
    --conf-medium:    #f59e0b;
    --conf-low:       #ef4444;

    --radius-sm:  6px;
    --radius-md:  12px;
    --radius-lg:  18px;
    --radius-xl:  24px;

    --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
    --shadow-glow: 0 0 40px rgba(79,70,229,0.2);
}

/* ═══════════════════════════════════════════
   GLOBAL RESET & BASE
═══════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ═══════════════════════════════════════════
   ANIMATED BACKGROUND GRID
═══════════════════════════════════════════ */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(79,70,229,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,70,229,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
    animation: gridShift 30s linear infinite;
}

@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 40px 40px; }
}

/* ═══════════════════════════════════════════
   MAIN CONTENT AREA
═══════════════════════════════════════════ */
[data-testid="stMain"],
.main .block-container {
    background: transparent !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
    position: relative;
    z-index: 1;
}

/* ═══════════════════════════════════════════
   PAGE HEADER
═══════════════════════════════════════════ */
.pip-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 28px 32px 24px;
    background: linear-gradient(135deg, var(--bg-elevated), var(--bg-surface));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    margin-bottom: 24px;
    box-shadow: var(--shadow-card), var(--shadow-glow);
    position: relative;
    overflow: hidden;
}

.pip-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(79,70,229,0.15) 0%, transparent 70%);
    pointer-events: none;
    animation: pulseOrb 6s ease-in-out infinite;
}

.pip-header::after {
    content: '';
    position: absolute;
    bottom: -60%;
    left: 20%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%);
    pointer-events: none;
    animation: pulseOrb 8s ease-in-out infinite reverse;
}

@keyframes pulseOrb {
    0%, 100% { transform: scale(1) translate(0, 0); opacity: 0.6; }
    50%       { transform: scale(1.2) translate(-10px, 10px); opacity: 1; }
}

.pip-header-icon {
    font-size: 2.2rem;
    filter: drop-shadow(0 0 12px rgba(79,70,229,0.7));
}

.pip-header-text h1 {
    font-size: clamp(1.4rem, 3vw, 2rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f1f5f9 30%, var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 4px !important;
    line-height: 1.1 !important;
}

.pip-header-text p {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0 !important;
}

.pip-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: 1px solid;
}

.pip-badge.live {
    background: rgba(16,185,129,0.12);
    border-color: rgba(16,185,129,0.4);
    color: #10b981;
}

/* ═══════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.25rem !important;
}

.sidebar-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
}

.sidebar-header-title {
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-secondary);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 14px 16px !important;
    margin-bottom: 10px !important;
    transition: border-color 0.2s, transform 0.2s;
}

[data-testid="stMetric"]:hover {
    border-color: var(--border-active) !important;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* Multiselect */
[data-testid="stMultiSelect"] > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    transition: border-color 0.2s;
}

[data-testid="stMultiSelect"] > div:focus-within {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.2) !important;
}

/* Stack labels */
[data-testid="stSidebar"] .stack-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 10px;
}

.stack-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    margin-bottom: 6px;
    font-size: 0.78rem;
    color: var(--text-secondary);
    transition: border-color 0.2s, color 0.2s;
}

.stack-row:hover {
    border-color: rgba(79,70,229,0.4);
    color: var(--text-primary);
}

.stack-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-indigo);
    flex-shrink: 0;
}

/* Clear button */
[data-testid="stSidebar"] button {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 10px !important;
    letter-spacing: 0.04em;
    transition: all 0.2s !important;
    margin-top: 4px !important;
}

[data-testid="stSidebar"] button:hover {
    background: rgba(239,68,68,0.1) !important;
    border-color: rgba(239,68,68,0.4) !important;
    color: #ef4444 !important;
    transform: translateY(-1px);
}

/* ═══════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    animation: messageSlideIn 0.3s cubic-bezier(0.16,1,0.3,1);
}

@keyframes messageSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([aria-label="user avatar"]) {
    justify-content: flex-end !important;
}

/* Avatar icons */
[data-testid="stChatMessageAvatar"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
}

/* Message content wrapper */
.message-bubble-user {
    background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple));
    border-radius: var(--radius-lg) var(--radius-sm) var(--radius-lg) var(--radius-lg);
    padding: 14px 18px;
    color: white;
    box-shadow: 0 4px 16px rgba(79,70,229,0.3);
    max-width: 80%;
    margin-left: auto;
}

.message-bubble-assistant {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm) var(--radius-lg) var(--radius-lg) var(--radius-lg);
    padding: 16px 20px;
    color: var(--text-primary);
    box-shadow: var(--shadow-card);
    line-height: 1.7;
}

/* Chat message paragraphs */
[data-testid="stChatMessage"] p {
    color: var(--text-primary) !important;
    line-height: 1.7 !important;
}

[data-testid="stChatMessage"] code {
    background: rgba(79,70,229,0.15) !important;
    color: var(--accent-cyan) !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 0.85em !important;
}

/* ═══════════════════════════════════════════
   CONFIDENCE BADGE
═══════════════════════════════════════════ */
.conf-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: 1px solid;
    margin: 10px 0 4px;
}

.conf-badge.high {
    background: rgba(16,185,129,0.12);
    border-color: rgba(16,185,129,0.4);
    color: var(--conf-high);
    box-shadow: 0 0 16px rgba(16,185,129,0.15);
}

.conf-badge.medium {
    background: rgba(245,158,11,0.12);
    border-color: rgba(245,158,11,0.4);
    color: var(--conf-medium);
    box-shadow: 0 0 16px rgba(245,158,11,0.15);
}

.conf-badge.low {
    background: rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.4);
    color: var(--conf-low);
    box-shadow: 0 0 16px rgba(239,68,68,0.15);
}

.conf-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: currentColor;
    animation: confPulse 2s ease infinite;
}

@keyframes confPulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.7); }
}

/* ═══════════════════════════════════════════
   CITATION EXPANDERS
═══════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 8px !important;
    transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
}

[data-testid="stExpander"]:hover {
    border-color: rgba(79,70,229,0.45) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(79,70,229,0.12) !important;
}

[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    letter-spacing: 0.02em;
    padding: 12px 16px !important;
    transition: color 0.2s;
}

[data-testid="stExpander"]:hover summary {
    color: var(--text-primary) !important;
}

[data-testid="stExpanderDetails"] {
    padding: 0 16px 14px !important;
}

.cite-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 8px;
    margin-bottom: 12px;
}

.cite-meta-item {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 8px 12px;
}

.cite-meta-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 3px;
}

.cite-meta-value {
    font-size: 0.8rem;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.cite-excerpt {
    background: var(--bg-base);
    border-left: 3px solid var(--accent-indigo);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 12px 16px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.6;
    white-space: pre-wrap;
}

.cite-score {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 8px;
}

.score-bar-bg {
    width: 80px;
    height: 4px;
    background: var(--bg-base);
    border-radius: 2px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-indigo), var(--accent-cyan));
    border-radius: 2px;
    transition: width 0.5s ease;
}

/* ═══════════════════════════════════════════
   CHAT INPUT
═══════════════════════════════════════════ */
[data-testid="stChatInput"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    box-shadow: 0 0 0 0 var(--accent-glow);
    transition: border-color 0.3s, box-shadow 0.3s !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 4px var(--accent-glow) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text-primary) !important;
    font-size: 0.92rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent-indigo) !important;
    border-radius: 50% !important;
    transition: all 0.2s !important;
}

[data-testid="stChatInputSubmitButton"] button:hover {
    background: var(--accent-purple) !important;
    transform: scale(1.1) !important;
}

/* ═══════════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 60px 32px;
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.empty-state-icon {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 24px rgba(79,70,229,0.5));
    margin-bottom: 20px;
}

.empty-state h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 10px;
}

.empty-state p {
    font-size: 0.88rem;
    color: var(--text-secondary);
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ═══════════════════════════════════════════
   SPINNER / THINKING STATE
═══════════════════════════════════════════ */
.thinking-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-active);
    border-radius: var(--radius-md);
    margin: 8px 0;
    animation: thinkingPulse 2s ease infinite;
}

@keyframes thinkingPulse {
    0%, 100% { border-color: rgba(79,70,229,0.4); box-shadow: 0 0 0 0 rgba(79,70,229,0.2); }
    50%       { border-color: rgba(79,70,229,0.8); box-shadow: 0 0 0 6px rgba(79,70,229,0); }
}

.thinking-dots span {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: var(--accent-indigo);
    border-radius: 50%;
    margin: 0 2px;
    animation: dotBounce 1.2s ease-in-out infinite;
}

.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotBounce {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40%            { transform: scale(1);   opacity: 1; }
}

/* ═══════════════════════════════════════════
   INFO / ERROR / WARNING ALERTS
═══════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border-left-width: 3px !important;
    font-size: 0.85rem !important;
}

/* ═══════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] hr,
hr {
    border-color: var(--border-subtle) !important;
    margin: 16px 0 !important;
}

/* ═══════════════════════════════════════════
   MARKDOWN OVERRIDES
═══════════════════════════════════════════ */
h1, h2, h3, h4 {
    color: var(--text-primary) !important;
}

strong { color: var(--text-primary) !important; }

a { color: var(--accent-cyan) !important; text-decoration: none !important; }
a:hover { text-decoration: underline !important; }

/* ═══════════════════════════════════════════
   MOBILE RESPONSIVE
═══════════════════════════════════════════ */
@media (max-width: 768px) {
    .pip-header { padding: 18px 20px 16px; flex-wrap: wrap; }
    .pip-header-text h1 { font-size: 1.3rem !important; }

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .cite-meta { grid-template-columns: 1fr 1fr; }
    .prompt-chips { flex-direction: column; align-items: center; }
    .chip { width: 100%; text-align: center; }
}

@media (max-width: 480px) {
    .pip-header { padding: 14px 16px; gap: 10px; }
    .pip-header-text h1 { font-size: 1.1rem !important; }
    .empty-state { padding: 40px 16px; }
    .cite-meta { grid-template-columns: 1fr; }
}

/* ═══════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb {
    background: var(--text-muted);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--accent-indigo); }

/* ═══════════════════════════════════════════
   REDUCED MOTION
═══════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Pipeline loader ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising policy intelligence engine…")
def load_pipeline():
    from policy_intel.pipeline import PolicyPipeline
    return PolicyPipeline()


# ── UI helpers ─────────────────────────────────────────────────────────────────
def _confidence_level(level: str) -> str:
    """Return CSS class name for a confidence level string."""
    return level.lower() if level.lower() in {"high", "medium", "low"} else "low"


def render_header() -> None:
    st.markdown(
        """
        <div class="pip-header">
            <div class="pip-header-icon">📋</div>
            <div class="pip-header-text">
                <h1>Policy Intelligence Platform</h1>
                <p>Hybrid retrieval · Cross-encoder reranking · Grounded citations · Confidence scoring</p>
            </div>
            <div style="margin-left:auto">
                <span class="pip-badge live">● Live</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_confidence_badge(level: str, score: float, rationale: str = "") -> None:
    css_class = _confidence_level(level)
    st.markdown(
        f"""
        <div class="conf-badge {css_class}">
            <span class="conf-dot"></span>
            Confidence: {level.upper()} &nbsp;·&nbsp; {score:.0%}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if rationale:
        st.caption(rationale)


def render_citations(citations: list[dict]) -> None:
    if not citations:
        st.info("No source excerpts were retrieved for this query.")
        return

    for idx, cite in enumerate(citations, start=1):
        label = cite.get("label", "Unknown source")
        with st.expander(f"⟨{idx}⟩ {label}"):
            # Meta grid
            meta_items = [
                ("Document", cite.get("source_doc", "N/A")),
                ("Page", cite.get("page_no", "N/A")),
                ("Clause", cite.get("clause_id", "N/A")),
            ]
            meta_html = "".join(
                f"""
                <div class="cite-meta-item">
                    <div class="cite-meta-label">{k}</div>
                    <div class="cite-meta-value">{v}</div>
                </div>
                """
                for k, v in meta_items
            )
            st.markdown(
                f'<div class="cite-meta">{meta_html}</div>',
                unsafe_allow_html=True,
            )

            # Excerpt
            excerpt = cite.get("excerpt", "")
            if excerpt:
                st.markdown(
                    f'<div class="cite-excerpt">{excerpt}</div>',
                    unsafe_allow_html=True,
                )

            # Relevance score bar
            rerank = cite.get("rerank_score")
            if rerank is not None:
                pct = min(max(rerank, 0), 1) * 100
                st.markdown(
                    f"""
                    <div class="cite-score">
                        <span>Relevance</span>
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:{pct:.1f}%"></div>
                        </div>
                        <span>{rerank:.3f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <h3>Ask anything about your policies</h3>
            <p>
                I'll retrieve the most relevant clauses across all indexed documents,
                rank them by relevance, and give you a grounded, cited answer.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(pipeline) -> list[str]:
    """Render sidebar, return selected policy filter list."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <span style="font-size:1.2rem"></span>
                <span class="sidebar-header-title">Policy Library</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        policies = pipeline.list_policies()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Policies", len(policies))
        with col2:
            st.metric("Chunks", len(pipeline.vector_store.chunks))

        st.markdown("**Filter by policy**")
        policy_options = [p["name"] for p in policies]
        selected = st.multiselect(
            "Filter by policy",
            options=policy_options,
            default=[],
            label_visibility="collapsed",
            help="Leave empty to search across all indexed policies.",
        )

        st.divider()

        st.markdown('<div class="stack-label">Retrieval stack</div>', unsafe_allow_html=True)
        stack = [
            ("Dense", "MiniLM-L12-v2"),
            ("Lexical", "BM25"),
            ("Reranker", "ms-marco-MiniLM-L-6-v2"),
            ("Generator", "Gemini 2.5 Flash"),
        ]
        for role, model in stack:
            st.markdown(
                f"""
                <div class="stack-row">
                    <div class="stack-dot"></div>
                    <span style="color:var(--text-muted);font-size:0.72rem;
                                 font-weight:700;text-transform:uppercase;
                                 letter-spacing:0.05em;width:64px;flex-shrink:0">{role}</span>
                    <span>{model}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        if st.button("🗑 Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    return selected


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "meta" in message:
                meta = message["meta"]
                conf = meta.get("confidence", {})
                render_confidence_badge(
                    level=conf.get("level", "unknown"),
                    score=conf.get("score", 0),
                    rationale=conf.get("rationale", ""),
                )
                render_citations(meta.get("citations", []))


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    render_header()

    # Guard: API key
    if not os.getenv("GEMINI_API_KEY"):
        st.error(
            "**GEMINI_API_KEY not found.** "
            "Add it to your `.env` file and restart the app."
        )
        st.stop()

    # Load pipeline
    try:
        pipeline = load_pipeline()
    except Exception as exc:
        st.error(f"**Pipeline initialisation failed:** {exc}")
        st.stop()

    # Sidebar
    selected_policies = render_sidebar(pipeline)

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history or empty state
    if st.session_state.messages:
        render_chat_history()
    else:
        render_empty_state()

    # Chat input
    question = st.chat_input("Ask a question about your insurance policies…")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving policy excerpts and generating answer…"):
                try:
                    result = pipeline.query_static(
                        question=question,
                        policy_filter=selected_policies or None,
                        mode="platform",
                    )

                    st.markdown(result.answer)

                    conf = result.confidence.to_dict() if result.confidence else {}
                    render_confidence_badge(
                        level=conf.get("level", "unknown"),
                        score=conf.get("score", 0),
                        rationale=conf.get("rationale", ""),
                    )
                    render_citations(result.citations)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": result.answer,
                            "meta": result.to_dict(),
                        }
                    )

                except Exception as exc:
                    st.error(f"**Query failed:** {exc}")


if __name__ == "__main__":
    main()