from __future__ import annotations

import streamlit as st

PLOT_TEMPLATE = "plotly_dark"
COLORS = ["#38bdf8", "#f59e0b", "#ef4444", "#22c55e", "#a855f7", "#14b8a6", "#f97316"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(circle at top left, #172554 0, #020617 38%, #020617 100%); }
        section[data-testid="stSidebar"] { background: #020617; border-right: 1px solid rgba(148, 163, 184, 0.22); }
        .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1480px; }
        .hero {
            padding: 30px 34px 32px 34px;
            border-radius: 26px;
            background:
              radial-gradient(circle at 10% 0%, rgba(56, 189, 248, .30), transparent 32%),
              linear-gradient(135deg, rgba(14, 165, 233, .24), rgba(15, 23, 42, .94) 60%, rgba(2, 6, 23, .96));
            border: 1px solid rgba(125, 211, 252, 0.28);
            box-shadow: 0 28px 80px rgba(2, 6, 23, 0.48), inset 0 1px 0 rgba(255,255,255,.06);
            margin-bottom: 18px;
            position: relative;
            overflow: hidden;
        }
        .hero:after {
            content: "";
            position: absolute;
            right: -90px;
            top: -110px;
            width: 330px;
            height: 330px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.10);
            filter: blur(2px);
        }
        .sidebar-brand {
            color: #dbeafe;
            text-align: center;
            font-weight: 800;
            font-size: 0.98rem;
            margin: 0.2rem 0 1rem 0;
            letter-spacing: 0.02em;
        }
        .hero-brand-row {
            display: flex;
            gap: 18px;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        .hero-logo {
            width: 96px;
            min-width: 96px;
            height: auto;
            filter: drop-shadow(0 8px 24px rgba(15, 23, 42, 0.45));
        }
        .hero-brand-copy { flex: 1; min-width: 0; }
        .hero-topline {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        .eyebrow { color:#93c5fd; font-weight:800; letter-spacing:.14em; text-transform:uppercase; font-size:.76rem; }
        .hero-pill {
            color:#dbeafe;
            font-weight:700;
            font-size:.76rem;
            letter-spacing:.04em;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(15, 23, 42, .72);
            border: 1px solid rgba(147, 197, 253, .28);
        }
        .hero h1 {
            margin: .15rem 0 .55rem 0;
            color: #f8fafc;
            font-size: clamp(1.95rem, 3.1vw, 3.7rem);
            line-height: 1.02;
            letter-spacing: -0.045em;
            font-weight: 900;
            max-width: none;
            white-space: nowrap;
            position: relative;
            z-index: 1;
        }
        .hero p { color:#dbeafe; font-size: 1.06rem; max-width: 1050px; margin:0; line-height:1.5; position: relative; z-index: 1; }
        .hero-subtext { margin-top: 8px !important; color: #bfdbfe !important; font-size: .98rem !important; opacity: .95; }
        @media (max-width: 1120px) { .hero h1 { white-space: normal; } }
        @media (max-width: 960px) { .hero-brand-row { flex-direction: column; align-items: flex-start; } .hero-logo { width: 84px; min-width: 84px; } .hero h1 { white-space: normal; } }
        .metric-card {
            background: rgba(15, 23, 42, 0.84);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 18px;
            padding: 18px 18px 16px 18px;
            height: 160px;
            box-shadow: 0 16px 40px rgba(2, 6, 23, 0.28);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
        }
        .compact-metric-card { height: 135px; }
        .metric-label { color:#94a3b8; font-size:.76rem; text-transform:uppercase; letter-spacing:.08em; font-weight:800; min-height: 18px; }
        .metric-value {
            color:#f8fafc;
            font-size: clamp(1.35rem, 2vw, 1.8rem);
            font-weight:900;
            margin-top:4px;
            line-height:1.12;
            letter-spacing: -0.035em;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        .compact-metric-value { font-size: clamp(1.25rem, 1.6vw, 1.55rem); }
        .metric-help { color:#cbd5e1; font-size:.84rem; margin-top:6px; line-height:1.42; }
        .action-card {
            background: rgba(15, 23, 42, 0.86);
            border: 1px solid rgba(56, 189, 248, 0.26);
            border-left: 4px solid #38bdf8;
            border-radius: 16px;
            padding: 15px 16px;
            margin-bottom: 12px;
            min-height: 114px;
        }
        .action-title { color:#f8fafc; font-size:1rem; font-weight:800; margin-bottom:4px; }
        .action-body { color:#cbd5e1; font-size:.92rem; line-height:1.45; }
        .section-title { color:#f8fafc; font-weight:900; margin: 24px 0 8px 0; letter-spacing: -0.03em; }
        .action-section-title { margin-top: 34px; }
        div[data-testid="stDataFrame"] { border-radius: 16px; overflow: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def plot_layout(title: str | None = None) -> dict:
    layout = {
        "template": PLOT_TEMPLATE,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#e5e7eb", "family": "Inter, sans-serif"},
        "margin": {"l": 30, "r": 20, "t": 58, "b": 30},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    }
    if title:
        layout["title"] = {"text": title, "font": {"size": 18, "color": "#f8fafc"}}
    return layout
