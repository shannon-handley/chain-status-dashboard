from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Chain Status Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
LOGO_PATHS = {
    "Great Wolf": BASE_DIR / "assets" / "great-wolf.svg",
    "Loews": BASE_DIR / "assets" / "loews.svg",
    "Pan Pacific": BASE_DIR / "assets" / "pan-pacific.svg",
}


def asset_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    encoded = b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


LOGO_URIS = {name: asset_data_uri(path) for name, path in LOGO_PATHS.items()}

try:
    CURRENT_VIEW_DATE = datetime.now(ZoneInfo("Australia/Sydney"))
except ZoneInfoNotFoundError:
    CURRENT_VIEW_DATE = datetime.now()

CURRENT_VIEW_LABEL = (
    f"{CURRENT_VIEW_DATE.strftime('%B')} {CURRENT_VIEW_DATE.day}, {CURRENT_VIEW_DATE.year}"
)

# ----------------------------
# Visual system
# ----------------------------

st.markdown(
    """
    <style>
        /* === Dark SaaS design tokens: adjust these to tune the dashboard palette quickly. === */
        :root {
            --app-bg: #070a12;
            --app-bg-soft: #0b1020;
            --card-bg: #101624;
            --card-bg-elevated: #151c2c;
            --card-bg-muted: #0d1320;
            --paper-bg: #ffffff;
            --paper-bg-soft: #f7f9fc;
            --paper-text: #172033;
            --paper-muted: #647089;
            --paper-border: #dce4ef;
            --text-main: #f4f7fb;
            --text-muted: #8f9bb2;
            --text-subtle: #647084;
            --border: rgba(148, 163, 184, 0.18);
            --border-strong: rgba(148, 163, 184, 0.28);
            --border-soft: rgba(148, 163, 184, 0.12);
            --accent: #7c5cff;
            --accent-2: #38bdf8;
            --accent-soft: rgba(124, 92, 255, 0.18);
            --live: #3ddc97;
            --live-soft: rgba(61, 220, 151, 0.14);
            --new: #f6b451;
            --new-soft: rgba(246, 180, 81, 0.15);
            --issue: #ff6b81;
            --issue-soft: rgba(255, 107, 129, 0.14);
            --shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
            --inner-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
            --radius: 12px;
            --font-stack: Inter, "SF Pro Display", "Segoe UI", Arial, sans-serif;
        }

        /* === Streamlit shell overrides. === */
        html, body, [class*="css"] {
            font-family: var(--font-stack);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124, 92, 255, 0.16), transparent 34rem),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 28rem),
                linear-gradient(180deg, var(--app-bg-soft), var(--app-bg) 38rem);
            color: var(--text-main);
        }

        .block-container {
            max-width: 1440px;
            padding: 1.2rem 2rem 2.4rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        div[data-testid="stToolbar"] {
            display: none;
        }

        h1, h2, h3, p {
            letter-spacing: 0;
        }

        hr {
            margin: 0.85rem 0 1rem;
            border-color: var(--border);
        }

        /* === Page header and card primitives. === */
        .app-header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
            margin: 0 0 0.9rem;
        }

        .app-title {
            margin: 0;
            color: var(--text-main);
            font-size: clamp(2.1rem, 4vw, 3rem);
            font-weight: 780;
            line-height: 1.05;
        }

        .app-caption {
            margin: 0.45rem 0 0;
            color: var(--text-muted);
            font-size: 0.98rem;
        }

        .as-of-pill {
            flex: 0 0 auto;
            color: #c9d3e6;
            background: rgba(255, 255, 255, 0.055);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.45rem 0.75rem;
            font-size: 0.82rem;
            white-space: nowrap;
        }

        .section-card {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0.012)),
                var(--card-bg);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin: 0.95rem 0;
            overflow: hidden;
            backdrop-filter: blur(14px);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--paper-bg) !important;
            border: 1px solid var(--paper-border) !important;
            border-radius: var(--radius) !important;
            box-shadow: 0 18px 44px rgba(6, 14, 28, 0.24);
            padding: 0 !important;
            overflow: hidden;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] .stHorizontalBlock {
            padding: 1rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] .section-heading {
            background: var(--paper-bg-soft);
            border-bottom: 1px solid var(--paper-border);
            box-shadow: none;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] .section-heading h2 {
            color: var(--paper-text);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] .section-heading span {
            color: var(--paper-muted);
        }

        .section-heading {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1rem 1rem 0.75rem;
            border-bottom: 1px solid var(--border);
            box-shadow: var(--inner-shadow);
        }

        .section-heading h2 {
            margin: 0;
            color: var(--text-main);
            font-size: 1.12rem;
            font-weight: 760;
        }

        .section-heading span {
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 680;
        }

        /* === Completion cards. === */
        .completion-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(230px, 1fr));
            gap: 0.8rem;
            padding: 1rem;
        }

        .completion-card {
            border: 1px solid var(--paper-border);
            border-radius: var(--radius);
            background: var(--paper-bg);
            padding: 0.9rem;
            box-shadow: 0 14px 30px rgba(6, 14, 28, 0.20);
        }

        .completion-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .completion-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-width: 0;
        }

        .completion-logo {
            width: 82px;
            height: 42px;
            object-fit: contain;
            flex: 0 0 auto;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.18rem;
        }

        .completion-name {
            color: var(--paper-text);
            font-weight: 760;
        }

        .completion-percent {
            color: var(--accent);
            font-size: 1.42rem;
            font-weight: 800;
        }

        .progress-track {
            width: 100%;
            height: 12px;
            overflow: hidden;
            border-radius: 999px;
            background: #e7edf5;
        }

        .progress-fill {
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--live), var(--accent-2));
            box-shadow: 0 0 18px rgba(61, 220, 151, 0.25);
        }

        .completion-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-top: 0.65rem;
            color: var(--paper-muted);
            font-size: 0.82rem;
            font-weight: 680;
        }

        /* === HTML status chart, matched to the local Codex dashboard. === */
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(220px, 1fr));
            gap: 0.8rem;
            padding: 1rem;
        }

        .portfolio-chart {
            display: grid;
            grid-template-rows: 1fr auto;
            min-height: 252px;
            border: 1px solid var(--paper-border);
            border-radius: var(--radius);
            padding: 0.75rem 0.75rem 0.65rem;
            background: var(--paper-bg);
            box-shadow: 0 14px 30px rgba(6, 14, 28, 0.20);
        }

        .bar-stage {
            display: flex;
            align-items: end;
            justify-content: center;
            gap: 1rem;
            min-height: 188px;
            padding: 0.75rem 0.6rem 0;
            border-bottom: 1px solid var(--paper-border);
            background:
                linear-gradient(to top, transparent 48px, rgba(100, 112, 137, 0.18) 49px, transparent 50px),
                linear-gradient(to top, transparent 96px, rgba(100, 112, 137, 0.18) 97px, transparent 98px),
                linear-gradient(to top, transparent 144px, rgba(100, 112, 137, 0.18) 145px, transparent 146px);
        }

        .bar-wrap {
            display: grid;
            justify-items: center;
            gap: 0.45rem;
            min-width: 82px;
        }

        .bar {
            width: 64px;
            min-height: 8px;
            border-radius: 6px 6px 0 0;
            display: flex;
            align-items: start;
            justify-content: center;
            color: #ffffff;
            font-weight: 780;
            padding-top: 0.4rem;
        }

        .bar.live {
            background: var(--live);
            box-shadow: 0 0 18px rgba(61, 220, 151, 0.20);
        }

        .bar.new {
            background: var(--new);
            box-shadow: 0 0 18px rgba(246, 180, 81, 0.18);
        }

        .bar-label {
            color: var(--paper-muted);
            font-size: 0.74rem;
            font-weight: 760;
            text-transform: uppercase;
        }

        .portfolio-label {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 0.7rem 0.25rem 0;
            font-weight: 760;
            color: var(--paper-text);
        }

        .portfolio-label span:last-child {
            color: var(--paper-muted);
        }

        /* === Native Streamlit widget polish. === */
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMultiSelect"]),
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stTextInput"]) {
            margin-bottom: 0.25rem;
        }

        label, div[data-testid="stWidgetLabel"] p {
            color: var(--text-muted) !important;
            font-size: 0.78rem !important;
            font-weight: 750 !important;
            text-transform: uppercase;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] label,
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stWidgetLabel"] p {
            color: var(--paper-muted) !important;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stTextInput"] input {
            background: rgba(255, 255, 255, 0.055) !important;
            border-color: var(--border) !important;
            border-radius: 7px !important;
            color: var(--text-main) !important;
            box-shadow: none !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="select"] > div,
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTextInput"] input {
            background: #ffffff !important;
            border-color: var(--paper-border) !important;
            color: var(--paper-text) !important;
        }

        div[data-baseweb="select"] > div:hover,
        div[data-testid="stTextInput"] input:hover {
            border-color: var(--border-strong) !important;
        }

        div[data-baseweb="select"] svg,
        div[data-testid="stTextInput"] svg {
            color: var(--text-muted) !important;
            fill: var(--text-muted) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] div[data-baseweb="select"] svg,
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTextInput"] svg {
            color: var(--paper-muted) !important;
            fill: var(--paper-muted) !important;
        }

        div[data-baseweb="tag"] {
            background: var(--accent-soft) !important;
            border: 1px solid rgba(124, 92, 255, 0.32) !important;
            border-radius: 999px !important;
            color: #eee9ff !important;
            font-weight: 720 !important;
        }

        div[data-baseweb="tag"] span {
            color: #eee9ff !important;
        }

        div[data-baseweb="tag"] svg {
            color: #c8bdff !important;
            fill: #c8bdff !important;
        }

        ul[role="listbox"] {
            background: var(--card-bg-elevated) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-main) !important;
        }

        li[role="option"] {
            color: var(--text-main) !important;
        }

        li[role="option"]:hover {
            background: rgba(124, 92, 255, 0.16) !important;
        }

        .stButton > button,
        div[data-testid="stDownloadButton"] button {
            min-height: 2.35rem;
            border: 1px solid rgba(124, 92, 255, 0.48);
            border-radius: 7px;
            color: #ffffff;
            background: linear-gradient(135deg, var(--accent), #5a3dce);
            font-weight: 750;
            box-shadow: 0 14px 28px rgba(124, 92, 255, 0.22);
        }

        .stButton > button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            border-color: rgba(124, 92, 255, 0.72);
            color: #ffffff;
            background: linear-gradient(135deg, #8d73ff, var(--accent));
        }

        /* === Status badges, tables, and upcoming migration cards. === */
        .table-wrap {
            width: 100%;
            overflow-x: auto;
            background: var(--paper-bg);
        }

        .styled-table {
            width: 100%;
            min-width: 920px;
            border-collapse: collapse;
            font-size: 0.88rem;
            color: var(--paper-text);
            background: var(--paper-bg);
        }

        .styled-table th,
        .styled-table td {
            text-align: left;
            vertical-align: top;
            border-bottom: 1px solid var(--paper-border);
            padding: 0.62rem 0.75rem;
        }

        .styled-table th {
            background: var(--paper-bg-soft);
            color: #596780;
            font-size: 0.74rem;
            font-weight: 780;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .styled-table td {
            color: var(--paper-text);
        }

        .styled-table tr:hover td {
            background: #f4f7ff;
        }

        .status-badge,
        .link-badge,
        .issue-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            padding: 0.2rem 0.55rem;
            font-size: 0.75rem;
            font-weight: 780;
            line-height: 1.35;
            white-space: nowrap;
        }

        .status-live {
            color: var(--live);
            background: var(--live-soft);
            border: 1px solid rgba(61, 220, 151, 0.22);
        }

        .status-new {
            color: var(--new);
            background: var(--new-soft);
            border: 1px solid rgba(246, 180, 81, 0.24);
        }

        .issue-badge {
            color: var(--issue);
            background: var(--issue-soft);
            border: 1px solid rgba(255, 107, 129, 0.24);
        }

        .link-badge {
            color: #4f3ed8;
            background: rgba(124, 92, 255, 0.12);
            border: 1px solid rgba(124, 92, 255, 0.22);
            text-decoration: none;
        }

        .muted-text {
            color: var(--text-muted);
        }

        .upcoming-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(210px, 1fr));
            gap: 0.8rem;
            padding: 1rem;
        }

        .upcoming-card {
            display: grid;
            gap: 0.75rem;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius);
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.014)),
                var(--card-bg-elevated);
            padding: 0.9rem;
            box-shadow: var(--inner-shadow);
        }

        .upcoming-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
        }

        .upcoming-top h3 {
            margin: 0;
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 780;
            line-height: 1.2;
        }

        .hotel-count {
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 0.22rem 0.55rem;
            color: #b9e7ff;
            background: rgba(56, 189, 248, 0.14);
            border: 1px solid rgba(56, 189, 248, 0.24);
            font-size: 0.72rem;
            font-weight: 780;
            white-space: nowrap;
        }

        .upcoming-label {
            display: block;
            color: var(--text-muted);
            font-size: 0.68rem;
            font-weight: 780;
            text-transform: uppercase;
        }

        .upcoming-value {
            color: #dce5f4;
            font-size: 0.86rem;
        }

        .plot-card {
            padding: 0.35rem 0.85rem 0.85rem;
        }

        .stCaptionContainer,
        .stMarkdown,
        .stMarkdown p {
            color: var(--text-muted);
        }

        @media (max-width: 980px) {
            .block-container {
                padding-left: 0.85rem;
                padding-right: 0.85rem;
            }

            .app-header {
                align-items: flex-start;
                flex-direction: column;
            }

            .completion-grid,
            .chart-grid,
            .upcoming-grid {
                grid-template-columns: 1fr;
            }

            .as-of-pill {
                white-space: normal;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.html(
    f"""
    <div class="app-header">
      <div>
        <h1 class="app-title">Chain Status Dashboard</h1>
        <p class="app-caption">Implementation projects, channel go-live status, and active issue tracking.</p>
      </div>
      <div class="as-of-pill">Current view: {CURRENT_VIEW_LABEL}</div>
    </div>
    """
)

# ----------------------------
# Source data
# ----------------------------

channels_data = [
    # Great Wolf
    {"portfolio": "Great Wolf", "project": "IBE", "channel": "IBE", "status": "LIVE", "go_live_date": "2026-04-15", "notes": "Finalized and handed over to Support."},
    {"portfolio": "Great Wolf", "project": "Groupon", "channel": "Groupon", "status": "LIVE", "go_live_date": "2026-05-07", "notes": "All batches migrated; stabilization in progress. Sporadic booking failures continue and are under investigation by OGTS/Dev."},
    {"portfolio": "Great Wolf", "project": "Expedia", "channel": "Expedia", "status": "LIVE", "go_live_date": "2026-05-07", "notes": "Pilot + batches 1-3 are live. Remaining properties on pause due to extra person rate issue, under review."},
    {"portfolio": "Great Wolf", "project": "HGV", "channel": "HGV", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Connectivity development finalized; partner delays remain."},
    {"portfolio": "Great Wolf", "project": "Google via DerbySoft Meta", "channel": "Google / DerbySoft Meta", "status": "LIVE", "go_live_date": "2026-06-03", "notes": "Validation in progress by DerbySoft."},
    {"portfolio": "Great Wolf", "project": "Booking.com for NIAGON", "channel": "Booking.com for NIAGON", "status": "LIVE", "go_live_date": "2026-06-02", "notes": "Separate onboarding track; go-live scheduled."},
    {"portfolio": "Great Wolf", "project": "GDS", "channel": "GDS", "status": "NEW", "go_live_date": "", "notes": "Separate workstream, planning in progress."},

    # Loews
    {"portfolio": "Loews", "project": "GDS", "channel": "GDS", "status": "LIVE", "go_live_date": "", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Costco Travel", "channel": "Costco Travel", "status": "LIVE", "go_live_date": "", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Expedia", "channel": "Expedia", "status": "LIVE", "go_live_date": "", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Booking.com", "channel": "Booking.com", "status": "LIVE", "go_live_date": "", "notes": "Operational; post-production issues remain."},
    {"portfolio": "Loews", "project": "HotelTonight via RateGain", "channel": "HotelTonight via RateGain", "status": "LIVE", "go_live_date": "", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Hopper", "channel": "Hopper", "status": "LIVE", "go_live_date": "", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Agoda", "channel": "Agoda", "status": "NEW", "go_live_date": "2026-05-29", "notes": "Pilot phase; scheduled to go live tomorrow."},
    {"portfolio": "Loews", "project": "Cendyn (IBE)", "channel": "Cendyn IBE", "status": "NEW", "go_live_date": "2026-06-12", "notes": "Final validation and CSV import/testing in progress."},

    # Pan Pacific
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Dida Travel", "status": "LIVE", "go_live_date": "2026-02-13", "notes": "Activated with switch partner (13 Feb); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Miki Tourist", "status": "LIVE", "go_live_date": "2026-02-13", "notes": "Activated with switch partner (13 Feb); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "TBO Holidays", "status": "LIVE", "go_live_date": "2026-02-13", "notes": "Activated with switch partner (13 Feb); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "WebBeds - Sunhotels", "status": "LIVE", "go_live_date": "2026-03-13", "notes": "Activated with switch partner (13-Mar-26 - PPYGN, 17-Mar-26 - PPDAC, 26-Mar-26 - remaining hotels); OTA test booking confirmed."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Luxury Escapes", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Flight Centre Travel", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Ly.com", "status": "LIVE", "go_live_date": "2026-05-21", "notes": "Activated with switch partner (21 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Hotelbeds", "status": "LIVE", "go_live_date": "2026-03-11", "notes": "Activated with switch partner (11-Mar-26 - PPYGN, 20-Apr-26 - remaining hotels); OTA test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Tiket", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Activated with switch partner (20 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Tidesquare", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Klook", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Activated with switch partner (20MAY except PRLGK, 29MAY-PRLGK); OTA test booking confirmed."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "G2 Travel", "status": "LIVE", "go_live_date": "2026-03-30", "notes": "Activated with switch partner (30 Mar); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Hong Kong Convergent", "status": "LIVE", "go_live_date": "2026-05-21", "notes": "Activated with switch partner (21 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "CN Travel Group", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Activated with switch partner (20 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Qiyouji", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Toptown Shanghai", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Keytel", "status": "LIVE", "go_live_date": "2026-04-20", "notes": "Activated with switch partner (20 Apr); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Tablet LLC", "status": "LIVE", "go_live_date": "2026-04-15", "notes": "Activated with switch partner (15 Apr); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Within Earth Holidays", "status": "LIVE", "go_live_date": "2026-05-21", "notes": "Activated with switch partner (21 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Expedia", "status": "LIVE", "go_live_date": "2026-01-27", "notes": "Activated with OTA (27 Jan); Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Booking.com", "status": "LIVE", "go_live_date": "2026-04-24", "notes": "Activated with OTA (24 Apr); Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Traveloka", "status": "LIVE", "go_live_date": "2026-03-13", "notes": "Activated with switch partner (13 Mar - PRLGK, 2 Apr - remaining hotels); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Rakuten", "status": "LIVE", "go_live_date": "2026-05-28", "notes": "Activated with switch partner (28MAY-PPSSIN,PRSSIN, 29MAY-PPYGN); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "MG Bedbank", "status": "LIVE", "go_live_date": "2026-05-26", "notes": "Activated with switch partner (26MAY-PRYGN, 29MAY-PPYGN,PRNYT,PRSSIN,PRPGB,PPDAC); ongoing validations and pending switch from OTA on 6 hotels."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Agoda", "status": "NEW", "go_live_date": "", "notes": "Ongoing testing/validations with Agoda"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Trip.com", "status": "NEW", "go_live_date": "", "notes": "Ongoing configurations/conversations between Trip.com and PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Nuitee", "status": "NEW", "go_live_date": "", "notes": "Ongoing testing/validations with Nuitee"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "TA Network", "status": "NEW", "go_live_date": "", "notes": "Pending switch update from OTA, then mapping from PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Roibos", "status": "NEW", "go_live_date": "", "notes": "Roibos in contact with PPHG regarding contractual details, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Goibibo & MakeMyTrip", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Emerging Travel", "status": "NEW", "go_live_date": "", "notes": "Awaiting confirmation from OTA to proceed before channel code can be added on PPHG properties"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Inntopia", "status": "NEW", "go_live_date": "", "notes": "PPHG advised channel will not be part of this batch."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Travco", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Dnata", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Meituan", "status": "NEW", "go_live_date": "", "notes": "PPHG advised this channel will go through Derbysoft channel manager"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Bakuun / RateDock", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
]

issues_data = [
    {
        "portfolio": "Great Wolf",
        "project": "Groupon",
        "issue_type": "Support / escalation",
        "link_type": "Slack",
        "link": "",
        "summary": "Recent booking failovers have been escalated to Oracle Support and are under review.",
    },
    {
        "portfolio": "Great Wolf",
        "project": "Expedia",
        "issue_type": "Product review",
        "link_type": "Slack",
        "link": "",
        "summary": "Extra-person calculation is under review by the Product Team.",
    },
    {
        "portfolio": "Great Wolf",
        "project": "HGV",
        "issue_type": "Partner delay",
        "link_type": "Slack",
        "link": "",
        "summary": "Oracle side is ready; testing is blocked by partner-side delays.",
    },
    {
        "portfolio": "Great Wolf",
        "project": "Google via DerbySoft Meta",
        "issue_type": "Dependency",
        "link_type": "Slack",
        "link": "",
        "summary": "Meta connectivity is being validated by DerbySoft before ARI push can continue.",
    },
    {
        "portfolio": "Pan Pacific",
        "project": "DSW & RSW channels",
        "issue_type": "Support / escalation",
        "link_type": "Slack",
        "link": "https://gbu-core.slack.com/archives/C07L44B259S/p1778727504326429",
        "summary": "OGTS Escalation | Ticket 260514-000492. DSW & RSW channels are missing for publications in OCC. Current workaround is to publish within Distribution UI.",
    },
    {
        "portfolio": "Loews",
        "project": "Booking.com",
        "issue_type": "Operational issue",
        "link_type": "JIRA",
        "link": "",
        "summary": "Reservations are not consistently interfacing into OPERA; email/contact configuration and reservation notes are being investigated.",
    },
    {
        "portfolio": "Loews",
        "project": "GDS",
        "issue_type": "JIRA",
        "link_type": "JIRA",
        "link": "",
        "summary": "Free night promotions on rate codes are not displaying or pricing correctly in GDS/Sabre.",
    },
    {
        "portfolio": "Loews",
        "project": "GDS",
        "issue_type": "JIRA",
        "link_type": "JIRA",
        "link": "",
        "summary": "Backfill GDS Line 1 channel description from negotiated rates import file.",
    },
    {
        "portfolio": "Loews",
        "project": "GDS",
        "issue_type": "Operational issue",
        "link_type": "Slack",
        "link": "",
        "summary": "Capital One rates are not showing available in Capital One.",
    },
]

upcoming_chains_data = [
    {
        "chain": "Minor",
        "hotels": "112 hotels",
        "go_live": "Sep 1, 2026",
        "channels": "SiteMinder, ORS > OCC Migration",
        "slack": "https://oracle.enterprise.slack.com/archives/C08FRQZAFMW",
    },
    {
        "chain": "Vail Resorts",
        "hotels": "62 hotels",
        "go_live": "Sep-26 (6 x Pilots) / Nov-26 (remaining hotels)",
        "channels": "Inntopia, Booking, Expedia, Trip, GDS",
        "slack": "https://oracle.enterprise.slack.com/archives/C0AHD3Y0QAW",
    },
    {
        "chain": "Voyages",
        "hotels": "8 hotels",
        "go_live": "TBC",
        "channels": "Booking, Expedia, WebBeds, HotelBeds, JTB Group, Luxury Escapes, Flight Centre, Trip.com",
        "slack": "",
    },
    {
        "chain": "MBS",
        "hotels": "Hotels TBC",
        "go_live": "Apr 1, 2027",
        "channels": "To be decided",
        "slack": "",
    },
]

df_channels = pd.DataFrame(channels_data)
df_issues = pd.DataFrame(issues_data)
df_upcoming_chains = pd.DataFrame(upcoming_chains_data)

# Normalize dates
df_channels["go_live_date"] = pd.to_datetime(
    df_channels["go_live_date"], errors="coerce"
).dt.date
df_channels["status"] = df_channels["status"].str.upper()


def safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return html_escape(str(value), quote=True)


def status_badge(status: str) -> str:
    status_value = safe_text(status).upper()
    status_class = "status-live" if status_value == "LIVE" else "status-new"
    return f'<span class="status-badge {status_class}">{status_value}</span>'


def section_heading(title: str, detail: str = "") -> str:
    detail_html = f"<span>{safe_text(detail)}</span>" if detail else ""
    return (
        '<div class="section-heading">'
        f"<h2>{safe_text(title)}</h2>"
        f"{detail_html}"
        "</div>"
    )


def render_completion_cards(rows: pd.DataFrame) -> str:
    cards = []
    for row in rows.itertuples(index=False):
        percent = int(round(float(row.completion) * 100))
        remaining = int(row.total_channels - row.live_channels)
        logo_uri = LOGO_URIS.get(row.portfolio, "")
        logo_html = (
            f'<img class="completion-logo" src="{safe_text(logo_uri)}" '
            f'alt="{safe_text(row.portfolio)} logo">'
            if logo_uri
            else ""
        )
        cards.append(
            f"""
            <article class="completion-card">
              <div class="completion-top">
                <div class="completion-brand">
                  {logo_html}
                  <span class="completion-name">{safe_text(row.portfolio)}</span>
                </div>
                <span class="completion-percent">{percent}%</span>
              </div>
              <div class="progress-track" aria-label="{safe_text(row.portfolio)} is {percent}% complete">
                <div class="progress-fill" style="width: {percent}%"></div>
              </div>
              <div class="completion-meta">
                <span>{int(row.live_channels)} of {int(row.total_channels)} LIVE</span>
                <span>{remaining} remaining</span>
              </div>
            </article>
            """
        )

    return (
        '<section class="section-card">'
        + section_heading("Project Completion")
        + '<div class="completion-grid">'
        + "".join(cards)
        + "</div></section>"
    )


def bar_markup(class_name: str, label: str, value: int, max_count: int) -> str:
    height = 8 if value == 0 else max(26, round((value / max_count) * 178))
    return (
        '<div class="bar-wrap">'
        f'<div class="bar {class_name}" style="height: {height}px" title="{safe_text(label)}: {value}">{value}</div>'
        f'<div class="bar-label">{safe_text(label)}</div>'
        "</div>"
    )


def render_status_chart(rows: pd.DataFrame, customers: list[str]) -> str:
    if rows.empty:
        chart_body = '<p class="muted-text" style="padding: 1rem;">No channels match the current filters.</p>'
    else:
        counts = []
        for customer in customers:
            customer_rows = rows[rows["portfolio"] == customer]
            live = int((customer_rows["status"] == "LIVE").sum())
            new = int((customer_rows["status"] == "NEW").sum())
            counts.append({"portfolio": customer, "live": live, "new": new})

        max_count = max(1, max(max(item["live"], item["new"]) for item in counts))
        chart_cards = []
        for item in counts:
            total = item["live"] + item["new"]
            chart_cards.append(
                f"""
                <article class="portfolio-chart">
                  <div class="bar-stage" aria-label="{safe_text(item["portfolio"])} channel status counts">
                    {bar_markup("live", "LIVE", item["live"], max_count)}
                    {bar_markup("new", "NEW", item["new"], max_count)}
                  </div>
                  <div class="portfolio-label">
                    <span>{safe_text(item["portfolio"])}</span>
                    <span>{total} channels</span>
                  </div>
                </article>
                """
            )
        chart_body = '<div class="chart-grid">' + "".join(chart_cards) + "</div>"

    return (
        '<section class="section-card">'
        + section_heading("Channels by Customer and Status")
        + chart_body
        + "</section>"
    )


def render_channel_table(rows: pd.DataFrame) -> str:
    if rows.empty:
        body = '<tr><td colspan="5" class="muted-text">No channels match the current filters.</td></tr>'
    else:
        row_html = []
        for _, row in rows.iterrows():
            row_html.append(
                f"""
            <tr>
              <td>{safe_text(row["Project"])}</td>
              <td>{safe_text(row["Channel"])}</td>
              <td>{status_badge(row["Status"])}</td>
              <td>{safe_text(row["Live / Proposed Go-Live"])}</td>
              <td>{safe_text(row["Notes"])}</td>
            </tr>
            """
            )
        body = "".join(row_html)

    return (
        '<section class="section-card">'
        + section_heading("Channel Status", f"{len(rows)} visible channels")
        + '<div class="table-wrap"><table class="styled-table">'
        "<thead><tr>"
        "<th>Project</th><th>Channel</th><th>Status</th><th>Live / Proposed Go-Live</th><th>Notes</th>"
        "</tr></thead><tbody>"
        + body
        + "</tbody></table></div></section>"
    )


def render_issues_table(rows: pd.DataFrame) -> str:
    row_html = []
    for _, row in rows.iterrows():
        row_html.append(
            f"""
        <tr>
          <td>{safe_text(row["Customer"])}</td>
          <td>{safe_text(row["Project"])}</td>
          <td><span class="issue-badge">{safe_text(row["Issue Type"])}</span></td>
          <td>{safe_text(row["Link Type"])}</td>
          <td>{render_link(row["Slack / JIRA Link"])}</td>
          <td>{safe_text(row["Summary"])}</td>
        </tr>
        """
        )
    body = "".join(row_html)
    return (
        '<section class="section-card">'
        + section_heading("Issue Tracker", f"{len(rows)} active issues")
        + '<div class="table-wrap"><table class="styled-table">'
        "<thead><tr>"
        "<th>Customer</th><th>Project</th><th>Issue Type</th><th>Link Type</th><th>Slack / JIRA Link</th><th>Summary</th>"
        "</tr></thead><tbody>"
        + body
        + "</tbody></table></div></section>"
    )


def render_link(url: object, label: str = "Open link") -> str:
    url_text = safe_text(url)
    if not url_text:
        return '<span class="muted-text">No link</span>'
    return (
        f'<a class="link-badge" href="{url_text}" target="_blank" '
        f'rel="noreferrer">{safe_text(label)}</a>'
    )


def render_upcoming_cards(rows: pd.DataFrame) -> str:
    cards = []
    for row in rows.itertuples(index=False):
        cards.append(
            f"""
            <article class="upcoming-card">
              <div class="upcoming-top">
                <h3>{safe_text(row.chain)}</h3>
                <span class="hotel-count">{safe_text(row.hotels)}</span>
              </div>
              <div>
                <span class="upcoming-label">Go Live</span>
                <strong class="upcoming-value">{safe_text(row.go_live)}</strong>
              </div>
              <div>
                <span class="upcoming-label">Channels</span>
                <span class="upcoming-value">{safe_text(row.channels)}</span>
              </div>
              {render_link(row.slack, "Open Slack")}
            </article>
            """
        )
    return (
        '<section class="section-card">'
        + section_heading("Upcoming Chain Migrations")
        + '<div class="upcoming-grid">'
        + "".join(cards)
        + "</div></section>"
    )


# ----------------------------
# Project completion tracker
# ----------------------------

completion_rows = (
    df_channels.groupby("portfolio", as_index=False)
    .agg(
        total_channels=("channel", "count"),
        live_channels=("status", lambda values: int((values == "LIVE").sum())),
    )
    .sort_values("portfolio")
)
completion_rows["completion"] = (
    completion_rows["live_channels"] / completion_rows["total_channels"]
).fillna(0)

st.html(render_completion_cards(completion_rows))

st.divider()

# ----------------------------
# Filters
# ----------------------------

with st.container(border=True):
    st.html(section_heading("Filters", "Refine the channel view"))
    left, right = st.columns([1, 2])

    with left:
        portfolio_filter = st.multiselect(
            "Customer",
            options=sorted(df_channels["portfolio"].unique()),
            default=sorted(df_channels["portfolio"].unique()),
        )

        status_filter = st.multiselect(
            "Status",
            options=sorted(df_channels["status"].unique()),
            default=sorted(df_channels["status"].unique()),
        )

    with right:
        search_text = st.text_input("Search channels / customers / notes", value="")

filtered_channels = df_channels[
    df_channels["portfolio"].isin(portfolio_filter)
    & df_channels["status"].isin(status_filter)
].copy()

if search_text.strip():
    mask = (
        filtered_channels["channel"].str.contains(search_text, case=False, na=False)
        | filtered_channels["portfolio"].str.contains(search_text, case=False, na=False)
        | filtered_channels["notes"].str.contains(search_text, case=False, na=False)
    )
    filtered_channels = filtered_channels[mask]

# ----------------------------
# Status visual
# ----------------------------

st.html(render_status_chart(filtered_channels, sorted(portfolio_filter)))

# ----------------------------
# Channels table
# ----------------------------

channels_display = filtered_channels.copy()
channels_display["project"] = channels_display["portfolio"]
channels_display["go_live_date"] = channels_display["go_live_date"].apply(
    lambda value: value.strftime("%Y-%m-%d") if pd.notna(value) else ""
)

channels_display = channels_display[
    ["project", "channel", "status", "go_live_date", "notes"]
]

channels_display = channels_display.rename(
    columns={
        "project": "Project",
        "channel": "Channel",
        "status": "Status",
        "go_live_date": "Live / Proposed Go-Live",
        "notes": "Notes",
    }
)

st.html(render_channel_table(channels_display))

# ----------------------------
# Issue tracker
# ----------------------------

issues_display = df_issues[df_issues["portfolio"].isin(portfolio_filter)].copy()
issues_display = issues_display.rename(
    columns={
        "portfolio": "Customer",
        "project": "Project",
        "issue_type": "Issue Type",
        "link_type": "Link Type",
        "link": "Slack / JIRA Link",
        "summary": "Summary",
    }
)

st.html(render_issues_table(issues_display))

# ----------------------------
# Upcoming chain migrations
# ----------------------------

st.html(render_upcoming_cards(df_upcoming_chains))

# ----------------------------
# Optional download
# ----------------------------

download_channels = df_channels.copy()
download_channels["project"] = download_channels["portfolio"]
download_channels = download_channels[
    ["project", "channel", "status", "go_live_date", "notes"]
]
csv = download_channels.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download channel data as CSV",
    data=csv,
    file_name="channel_status_data.csv",
    mime="text/csv",
)

st.caption("Edit the data blocks at the top of the file to update the dashboard content.")
