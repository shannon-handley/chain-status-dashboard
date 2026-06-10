from __future__ import annotations

from base64 import b64encode
from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote
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
STATUS_ORDER = ["LIVE", "IN PROGRESS", "NEW"]
STATUS_SYMBOLS = {"LIVE": "✓", "IN PROGRESS": "◆", "NEW": "▲"}
SEVERITY_SYMBOLS = {"Critical": "!", "High": "▲", "Medium": "●", "Low": "•", "None": "○"}
HEALTH_SYMBOLS = {
    "Healthy": "✓",
    "Attention Needed": "●",
    "At Risk": "▲",
    "Escalated": "!",
}
SECTION_ICONS = {
    "Project Completion": "▣",
    "Channels by Customer and Status": "▥",
    "Channel Status": "☷",
    "Upcoming Chain Migrations": "↗",
    "Customer Health": "◎",
    "Ownership Matrix": "◇",
    "Issue Tracker": "!",
    "Open Issues & Blockers": "!",
    "Executive Escalations": "▲",
    "Risk Feed": "◌",
}

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
            --progress: #7c5cff;
            --progress-soft: rgba(124, 92, 255, 0.14);
            --new: #f6b451;
            --new-soft: rgba(246, 180, 81, 0.15);
            --issue: #ff6b81;
            --issue-soft: rgba(255, 107, 129, 0.14);
            --critical: #ef4444;
            --warning: #f97316;
            --success: #22c55e;
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
                radial-gradient(circle at top left, rgba(124, 92, 255, 0.08), transparent 18rem),
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
            display: inline-flex;
            align-items: center;
            gap: 0.48rem;
            margin: 0;
            color: var(--text-main);
            font-size: 1.12rem;
            font-weight: 760;
        }

        .section-heading .section-detail {
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 680;
        }

        .section-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.65rem;
            height: 1.65rem;
            border-radius: 999px;
            color: #d7efff;
            background: linear-gradient(135deg, rgba(124, 92, 255, 0.32), rgba(56, 189, 248, 0.24));
            border: 1px solid rgba(148, 163, 184, 0.22);
            font-size: 0.82rem;
            box-shadow: 0 10px 24px rgba(56, 189, 248, 0.12);
        }

        /* === Completion cards. === */
        .completion-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(230px, 1fr));
            gap: 0.8rem;
            padding: 1rem;
        }

        .completion-card {
            display: block;
            border: 1px solid var(--paper-border);
            border-radius: var(--radius);
            background:
                radial-gradient(circle at top right, rgba(124, 92, 255, 0.10), transparent 12rem),
                linear-gradient(180deg, #ffffff, #f9fbff);
            padding: 0.9rem;
            box-shadow: 0 14px 30px rgba(6, 14, 28, 0.20);
            border-top: 4px solid var(--accent-2);
            text-decoration: none;
            transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
        }

        .completion-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.55);
            box-shadow: 0 18px 38px rgba(6, 14, 28, 0.28);
        }

        .completion-card.selected {
            border-color: rgba(124, 92, 255, 0.62);
            box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.18), 0 18px 38px rgba(6, 14, 28, 0.26);
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
            color: #6d4eff;
            font-size: 1.42rem;
            font-weight: 800;
        }

        .completion-status {
            display: inline-flex;
            align-items: center;
            gap: 0.28rem;
            margin-top: -0.15rem;
            color: var(--paper-muted);
            font-size: 0.74rem;
            font-weight: 780;
            text-transform: uppercase;
        }

        .completion-status .status-badge {
            padding: 0.12rem 0.42rem;
            font-size: 0.68rem;
        }

        .completion-status .status-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            background: var(--live);
            box-shadow: 0 0 0 4px rgba(61, 220, 151, 0.16);
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

        .completion-meta span {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .completion-health-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin: 0.75rem 0 0.35rem;
        }

        .completion-health-stat {
            display: grid;
            gap: 0.12rem;
        }

        .completion-health-stat strong {
            color: var(--paper-text);
            font-size: 1rem;
        }

        .completion-health-stat span {
            color: var(--paper-muted);
            font-size: 0.66rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .completion-detail {
            margin: 0.45rem 0 0;
            color: var(--paper-muted);
            font-size: 0.78rem;
            line-height: 1.42;
        }

        .completion-detail strong {
            color: #475569;
        }

        .selection-note {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 0 1rem 1rem;
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 680;
        }

        .selection-note a {
            color: #d7efff;
            text-decoration: none;
            border-bottom: 1px solid rgba(56, 189, 248, 0.45);
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
            background:
                radial-gradient(circle at top, rgba(56, 189, 248, 0.07), transparent 13rem),
                var(--paper-bg);
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
            min-width: 92px;
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
            background: linear-gradient(180deg, #4ade80, var(--live));
            box-shadow: 0 0 18px rgba(61, 220, 151, 0.20);
        }

        .bar.in-progress {
            background: linear-gradient(180deg, #9b87ff, var(--progress));
            box-shadow: 0 0 18px rgba(124, 92, 255, 0.20);
        }

        .bar.new {
            background: linear-gradient(180deg, #ffd072, var(--new));
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

        .portfolio-footnote {
            display: flex;
            gap: 0.4rem;
            align-items: center;
            color: var(--paper-muted);
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.1rem 0.25rem 0;
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

        /* Make filter controls readable even when Streamlit changes container wrappers. */
        div[data-testid="stMultiSelect"] div[data-baseweb="select"],
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div,
        div[data-testid="stMultiSelect"] [role="combobox"] {
            background: #f8fafc !important;
            border-color: #cbd5e1 !important;
            color: var(--paper-text) !important;
        }

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
            min-height: 2.55rem;
            box-sizing: border-box !important;
            overflow: visible !important;
            padding: 0.28rem 0.45rem 0.28rem 0.65rem !important;
            box-shadow: 0 10px 22px rgba(6, 14, 28, 0.10) !important;
        }

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div > div {
            overflow: visible !important;
        }

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div:focus-within {
            border-color: #7c5cff !important;
            box-shadow: 0 0 0 3px rgba(124, 92, 255, 0.18) !important;
        }

        div[data-testid="stMultiSelect"] input {
            color: var(--paper-text) !important;
            caret-color: var(--paper-text) !important;
        }

        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {
            margin: 0.12rem 0.18rem 0.12rem 0 !important;
            overflow: visible !important;
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

        div[data-testid="stMultiSelect"] div[data-baseweb="select"] svg {
            color: #475569 !important;
            fill: #475569 !important;
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
            position: sticky;
            top: 0;
            z-index: 2;
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

        .badge-symbol {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 0.28rem;
            font-size: 0.72rem;
            line-height: 1;
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

        .status-in-progress {
            color: var(--progress);
            background: var(--progress-soft);
            border: 1px solid rgba(124, 92, 255, 0.24);
        }

        .severity-critical,
        .health-escalated {
            color: #dc2626;
            background: rgba(220, 38, 38, 0.12);
            border: 1px solid rgba(220, 38, 38, 0.28);
        }

        .severity-high,
        .health-at-risk {
            color: #ea580c;
            background: rgba(234, 88, 12, 0.13);
            border: 1px solid rgba(234, 88, 12, 0.28);
        }

        .severity-medium,
        .health-attention-needed {
            color: #ca8a04;
            background: rgba(202, 138, 4, 0.14);
            border: 1px solid rgba(202, 138, 4, 0.28);
        }

        .severity-low,
        .health-healthy {
            color: #059669;
            background: rgba(5, 150, 105, 0.12);
            border: 1px solid rgba(5, 150, 105, 0.26);
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

        div[data-testid="stMetric"] {
            min-height: 112px;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018)),
                var(--card-bg-elevated);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0.8rem 0.95rem;
            box-shadow: var(--shadow);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--text-muted) !important;
            font-size: 0.75rem !important;
            font-weight: 780 !important;
            text-transform: uppercase;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-main);
            font-weight: 820;
        }

        .rule-grid,
        .health-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(170px, 1fr));
            gap: 0.8rem;
            padding: 1rem;
        }

        .health-grid {
            grid-template-columns: repeat(3, minmax(260px, 1fr));
        }

        .rule-chip,
        .health-card {
            border-radius: var(--radius);
            background: var(--paper-bg);
            border: 1px solid var(--paper-border);
            color: var(--paper-text);
            box-shadow: 0 14px 30px rgba(6, 14, 28, 0.18);
        }

        .rule-chip {
            padding: 0.8rem;
        }

        .rule-chip strong,
        .health-card h3 {
            display: block;
            margin: 0 0 0.35rem;
            color: var(--paper-text);
            font-size: 0.95rem;
        }

        .rule-chip span,
        .health-meta,
        .health-detail {
            color: var(--paper-muted);
            font-size: 0.8rem;
        }

        .health-card {
            padding: 0.95rem;
            border-left: 5px solid #94a3b8;
        }

        .health-card.health-escalated {
            border-left-color: #dc2626;
        }

        .health-card.health-at-risk {
            border-left-color: #ea580c;
        }

        .health-card.health-attention-needed {
            border-left-color: #ca8a04;
        }

        .health-card.health-healthy {
            border-left-color: #059669;
        }

        .health-top,
        .health-counts,
        .ownership-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.65rem;
        }

        .health-counts {
            margin: 0.75rem 0;
        }

        .mini-stat {
            display: grid;
            gap: 0.1rem;
        }

        .mini-stat strong {
            color: var(--paper-text);
            font-size: 1.05rem;
        }

        .mini-stat span {
            color: var(--paper-muted);
            font-size: 0.68rem;
            font-weight: 780;
            text-transform: uppercase;
        }

        .attention-strip {
            margin: 1rem;
            padding: 0.85rem 1rem;
            border-radius: var(--radius);
            background: rgba(220, 38, 38, 0.12);
            border: 1px solid rgba(220, 38, 38, 0.34);
            color: #fecaca;
            font-weight: 720;
        }

        .owner-missing {
            color: #fecaca;
            background: rgba(220, 38, 38, 0.16);
            border: 1px solid rgba(220, 38, 38, 0.30);
            border-radius: 999px;
            padding: 0.18rem 0.48rem;
            font-size: 0.72rem;
            font-weight: 780;
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
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 10rem),
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

        .upcoming-name {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
        }

        .upcoming-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.6rem;
            height: 1.6rem;
            border-radius: 8px;
            color: #d7efff;
            background: rgba(56, 189, 248, 0.14);
            border: 1px solid rgba(56, 189, 248, 0.22);
            font-size: 0.78rem;
            font-weight: 820;
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
            .upcoming-grid,
            .health-grid,
            .rule-grid {
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
    {"portfolio": "Great Wolf", "project": "HGV", "channel": "HGV", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Channel live, validation in progress by GWR Team."},
    {"portfolio": "Great Wolf", "project": "Google via DerbySoft Meta", "channel": "Google / DerbySoft Meta", "status": "LIVE", "go_live_date": "2026-06-03", "notes": "Channel live, validation in progress by GWR Team."},
    {"portfolio": "Great Wolf", "project": "Booking.com for NIAGON", "channel": "Booking.com for NIAGON", "status": "LIVE", "go_live_date": "2026-06-02", "notes": "Channel live, validation in progress by GWR Team."},
    {"portfolio": "Great Wolf", "project": "GDS", "channel": "GDS", "status": "NEW", "go_live_date": "", "notes": "Separate workstream, planning in progress."},

    # Loews
    {"portfolio": "Loews", "project": "GDS", "channel": "GDS", "status": "LIVE", "go_live_date": "2026-05-08", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Costco Travel", "channel": "Costco Travel", "status": "LIVE", "go_live_date": "2026-05-07", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Expedia", "channel": "Expedia", "status": "LIVE", "go_live_date": "2026-05-12", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Booking.com", "channel": "Booking.com", "status": "LIVE", "go_live_date": "2026-05-13", "notes": "Operational; post-production issues remain."},
    {"portfolio": "Loews", "project": "HotelTonight via RateGain", "channel": "HotelTonight via RateGain", "status": "LIVE", "go_live_date": "2026-05-18", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Hopper", "channel": "Hopper", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Agoda", "channel": "Agoda", "status": "LIVE", "go_live_date": "2026-05-27", "notes": "Operational across all 16 properties."},
    {"portfolio": "Loews", "project": "Cendyn (IBE)", "channel": "Cendyn IBE", "status": "LIVE", "go_live_date": "2026-06-09", "notes": "Live as of 9 June 2026 after additional configuration / development work."},

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
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Agoda", "status": "IN PROGRESS", "go_live_date": "", "notes": "Ongoing testing/validations with Agoda"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Trip.com", "status": "IN PROGRESS", "go_live_date": "", "notes": "Ongoing configurations/conversations between Trip.com and PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Nuitee", "status": "IN PROGRESS", "go_live_date": "", "notes": "Ongoing testing/validations with Nuitee"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "TA Network", "status": "NEW", "go_live_date": "", "notes": "Pending switch update from OTA, then mapping from PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Roibos", "status": "NEW", "go_live_date": "", "notes": "Roibos in contact with PPHG regarding contractual details, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Goibibo & MakeMyTrip", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Emerging Travel", "status": "NEW", "go_live_date": "", "notes": "Awaiting confirmation from OTA to proceed before channel code can be added on PPHG properties"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Inntopia", "status": "NEW", "go_live_date": "", "notes": "PPHG advised channel will not be part of this batch."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Travco", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Dnata", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Bakuun / RateDock", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
]

issues_data = [
    {
        "portfolio": "Great Wolf",
        "project": "Groupon",
        "issue_type": "Support / escalation",
        "link_type": "Slack",
        "link": "https://gbu-core.slack.com/archives/C08FAGCS275/p1778279062722849",
        "summary": "Recent booking failovers have been escalated to Oracle Support and are under review.",
    },
    {
        "portfolio": "Great Wolf",
        "project": "Expedia",
        "issue_type": "Product review",
        "link_type": "Slack",
        "link": "https://oracle-one.slack.com/archives/C0927KWHJTG/p1778847783945629",
        "summary": "Extra-person calculation is under review by the Product Team.",
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

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "None": 0}
HEALTH_ORDER = {
    "Escalated": 4,
    "At Risk": 3,
    "Attention Needed": 2,
    "Healthy": 1,
}
CUSTOMER_PROFILES = {
    "Great Wolf": {
        "accountable_owner": "GWR Team",
        "support_team": "OGTS / Dev",
        "escalation_contact": "Oracle Support",
        "next_milestone": "Stabilize live channels and complete GDS planning",
        "target_date": "2026-06-05",
    },
    "Loews": {
        "accountable_owner": "Loews Onboarding Team",
        "support_team": "Distribution Engineering",
        "escalation_contact": "Oracle Support",
        "next_milestone": "Post-go-live validation and open issue follow-up",
        "target_date": "2026-06-09",
    },
    "Pan Pacific": {
        "accountable_owner": "PPHG Team",
        "support_team": "OGTS / Distribution UI",
        "escalation_contact": "OGTS Escalation",
        "next_milestone": "Resolve OCC publication gaps and progress OTA validations",
        "target_date": "2026-06-04",
    },
}

ISSUE_ENRICHMENT = {
    ("Great Wolf", "Groupon"): {
        "severity": "High",
        "owner": "OGTS / Dev",
        "accountable_owner": "GWR Team",
        "support_team": "Oracle Support",
        "escalation_contact": "Oracle Support",
        "created_at": "2026-06-02",
        "due_date": "2026-06-04",
        "impact": "Sporadic booking failures affecting live Groupon traffic.",
        "next_action": "Confirm root cause and publish stabilization plan.",
        "escalation_status": "Escalated",
        "blocked": True,
        "escalated": True,
    },
    ("Great Wolf", "Expedia"): {
        "severity": "High",
        "owner": "Product Team",
        "accountable_owner": "GWR Team",
        "support_team": "OGTS / Dev",
        "escalation_contact": "Product Lead",
        "created_at": "2026-05-07",
        "due_date": "2026-06-05",
        "impact": "Remaining Expedia properties are paused pending extra-person rate decision.",
        "next_action": "Product Team to confirm calculation decision and resume migration path.",
        "escalation_status": "Watch",
        "blocked": True,
        "escalated": False,
    },
    ("Pan Pacific", "DSW & RSW channels"): {
        "severity": "Critical",
        "owner": "OGTS Escalation",
        "accountable_owner": "PPHG Team",
        "support_team": "Distribution UI",
        "escalation_contact": "OGTS Escalation",
        "created_at": "2026-05-14",
        "due_date": "2026-06-04",
        "impact": "DSW & RSW channels are missing for OCC publication workflows.",
        "next_action": "Restore missing channels in OCC; continue Distribution UI workaround until fixed.",
        "escalation_status": "Escalated",
        "blocked": True,
        "escalated": True,
    },
    ("Loews", "Booking.com"): {
        "severity": "High",
        "owner": "Oracle Support",
        "accountable_owner": "Loews Onboarding Team",
        "support_team": "OPERA Interface Team",
        "escalation_contact": "Oracle Support",
        "created_at": "2026-05-13",
        "due_date": "2026-06-06",
        "impact": "Reservations are not consistently interfacing into OPERA.",
        "next_action": "Complete email/contact configuration and reservation-note investigation.",
        "escalation_status": "Watch",
        "blocked": False,
        "escalated": False,
    },
    ("Loews", "GDS"): {
        "severity": "Medium",
        "owner": "GDS Support",
        "accountable_owner": "Loews Onboarding Team",
        "support_team": "Sabre / GDS",
        "escalation_contact": "Oracle Support",
        "created_at": "2026-05-15",
        "due_date": "2026-06-07",
        "impact": "GDS pricing, promotion, or negotiated-rate display issues may affect partner availability.",
        "next_action": "Resolve open GDS cases and validate partner display.",
        "escalation_status": "In Progress",
        "blocked": False,
        "escalated": False,
    },
}


def safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return html_escape(str(value), quote=True)


def status_badge(status: str) -> str:
    status_value = safe_text(status).upper()
    status_class = {
        "LIVE": "status-live",
        "IN PROGRESS": "status-in-progress",
        "NEW": "status-new",
    }.get(status_value, "status-new")
    symbol = STATUS_SYMBOLS.get(status_value, "•")
    return (
        f'<span class="status-badge {status_class}">'
        f'<span class="badge-symbol">{safe_text(symbol)}</span>{status_value}</span>'
    )


def section_heading(title: str, detail: str = "") -> str:
    icon = SECTION_ICONS.get(title, "•")
    detail_html = f'<span class="section-detail">{safe_text(detail)}</span>' if detail else ""
    return (
        '<div class="section-heading">'
        f'<h2><span class="section-icon">{safe_text(icon)}</span>{safe_text(title)}</h2>'
        f"{detail_html}"
        "</div>"
    )


def build_completion_rows(channels: pd.DataFrame) -> pd.DataFrame:
    if channels.empty:
        return pd.DataFrame(
            columns=[
                "portfolio",
                "total_channels",
                "live_channels",
                "in_progress_channels",
                "new_channels",
                "completion",
            ]
        )

    rows = []
    for customer in sorted(channels["portfolio"].unique()):
        customer_rows = channels[channels["portfolio"] == customer]
        total = int(len(customer_rows))
        live = int((customer_rows["status"] == "LIVE").sum())
        in_progress = int((customer_rows["status"] == "IN PROGRESS").sum())
        new = int((customer_rows["status"] == "NEW").sum())
        rows.append(
            {
                "portfolio": customer,
                "total_channels": total,
                "live_channels": live,
                "in_progress_channels": in_progress,
                "new_channels": new,
                "completion": live / total if total else 0,
            }
        )
    return pd.DataFrame(rows)


def completion_issue_records(records: pd.DataFrame, customer: str) -> pd.DataFrame:
    if records.empty:
        return pd.DataFrame()
    return records[
        (records["customer"] == customer)
        & records["record_type"].isin(["issue", "risk_signal"])
    ].sort_values(["risk_score", "age_days"], ascending=False)


def issue_summary_label(row: pd.Series) -> str:
    customer = str(row.get("customer", ""))
    project = str(row.get("project", ""))
    title = str(row.get("title", ""))
    status = str(row.get("status", ""))
    description = str(row.get("description", ""))
    summary = str(row.get("impact", "") or description)
    searchable_summary = f"{summary} {description}"

    if customer == "Great Wolf" and project == "Groupon":
        return "Groupon booking failure - OGTS escalation"
    if customer == "Great Wolf" and project == "Expedia":
        return "Expedia extra-person error - Dev Team escalation"
    if customer == "Pan Pacific" and project == "DSW & RSW channels":
        return "DSW & RSW publication gaps - OGTS escalation"
    if customer == "Loews" and project == "Booking.com":
        return "Booking.com reservation interface issue"
    if customer == "Loews" and project == "GDS":
        if "Free night" in searchable_summary:
            return "GDS free-night pricing issue"
        if "Backfill" in searchable_summary:
            return "GDS negotiated-rate backfill"
        if "Capital One" in searchable_summary:
            return "Capital One rate availability"
        return "GDS display/pricing issue"

    if project == "Channel Status":
        channels = description.split(":", 1)[0].strip()
        if status == "IN PROGRESS":
            return f"{channels} - in progress"
        if status == "NEW":
            return f"{channels} - still to onboard"
        return f"{channels} - follow-up needed"

    return title or project or "Issue requires follow-up"


def customer_issue_summary(records: pd.DataFrame, customer: str, max_items: int = 4) -> str:
    customer_issues = completion_issue_records(records, customer)
    if customer_issues.empty:
        return "No tracked issues."

    labels = []
    for _, issue in customer_issues.iterrows():
        label = issue_summary_label(issue)
        if label not in labels:
            labels.append(label)

    visible_labels = labels[:max_items]
    remainder = len(labels) - len(visible_labels)
    summary = " / ".join(visible_labels)
    if remainder > 0:
        summary += f" / +{remainder} more"
    return summary


def query_customer(customer_options: list[str]) -> str:
    try:
        raw_value = st.query_params.get("customer", "")
    except Exception:
        raw_value = ""
    if isinstance(raw_value, list):
        raw_value = raw_value[0] if raw_value else ""
    return raw_value if raw_value in customer_options else ""


def render_completion_cards(
    rows: pd.DataFrame,
    health_rows: pd.DataFrame,
    records: pd.DataFrame,
    selected_customer: str = "",
) -> str:
    if rows.empty:
        body = '<p class="muted-text" style="padding:1rem;">No customers match the active filters.</p>'
    else:
        health_lookup = {
            row.customer: row
            for row in health_rows.itertuples(index=False)
        }
        cards = []
        for row in rows.itertuples(index=False):
            percent = int(round(float(row.completion) * 100))
            remaining = int(row.total_channels - row.live_channels)
            health = health_lookup.get(row.portfolio)
            health_state = getattr(health, "health_state", "Attention Needed")
            health_class = f"health-{str(health_state).lower().replace(' ', '-')}"
            health_symbol = HEALTH_SYMBOLS.get(health_state, "•")
            issue_count = int(len(completion_issue_records(records, row.portfolio)))
            issue_summary = customer_issue_summary(records, row.portfolio)
            logo_uri = LOGO_URIS.get(row.portfolio, "")
            if remaining == 0:
                status_label = "Complete"
            elif int(row.in_progress_channels) > 0:
                status_label = "In progress"
            else:
                status_label = "Action needed"
            selected_class = " selected" if row.portfolio == selected_customer else ""
            customer_url = f"?customer={quote(row.portfolio)}"
            logo_html = (
                f'<img class="completion-logo" src="{safe_text(logo_uri)}" '
                f'alt="{safe_text(row.portfolio)} logo">'
                if logo_uri
                else ""
            )
            cards.append(
                f"""
                <a class="completion-card{selected_class}" href="{safe_text(customer_url)}" aria-label="Show {safe_text(row.portfolio)} summary">
                  <div class="completion-top">
                    <div class="completion-brand">
                      {logo_html}
                      <div>
                        <div class="completion-name">{safe_text(row.portfolio)}</div>
                        <div class="completion-status">
                          <span class="status-dot"></span>{safe_text(status_label)}
                          <span class="status-badge {health_class}"><span class="badge-symbol">{safe_text(health_symbol)}</span>{safe_text(health_state)}</span>
                        </div>
                      </div>
                    </div>
                    <span class="completion-percent">{percent}%</span>
                  </div>
                  <div class="progress-track" aria-label="{safe_text(row.portfolio)} is {percent}% live">
                    <div class="progress-fill" style="width: {percent}%"></div>
                  </div>
                  <div class="completion-meta">
                    <span>{safe_text(STATUS_SYMBOLS["LIVE"])} {int(row.live_channels)} of {int(row.total_channels)} LIVE</span>
                    <span>{remaining} remaining</span>
                  </div>
                  <div class="completion-health-grid">
                    <span class="completion-health-stat"><strong>{int(row.live_channels)}/{int(row.total_channels)}</strong><span>Live</span></span>
                    <span class="completion-health-stat"><strong>{remaining}</strong><span>In progress</span></span>
                    <span class="completion-health-stat"><strong>{issue_count}</strong><span>Issues</span></span>
                  </div>
                  <p class="completion-detail"><strong>Issue Summary:</strong> {safe_text(issue_summary)}</p>
                </a>
                """
            )
        focus_message = (
            f"Showing issue tracker and channel status for {safe_text(selected_customer)}."
            if selected_customer
            else "Click a customer card to focus the issue tracker and channel status."
        )
        clear_link = '<a href="?">Show all customers</a>' if selected_customer else ""
        body = (
            '<div class="completion-grid">'
            + "".join(cards)
            + "</div>"
            + f'<div class="selection-note"><span>{focus_message}</span>{clear_link}</div>'
        )

    return (
        '<section class="section-card">'
        + section_heading("Project Completion", "Live channels, in-progress channels, and tracked issues")
        + body
        + "</section>"
    )


def bar_markup(class_name: str, label: str, value: int, max_count: int) -> str:
    height = 8 if value == 0 else max(26, round((value / max_count) * 178))
    symbol = STATUS_SYMBOLS.get(label, "•")
    return (
        '<div class="bar-wrap">'
        f'<div class="bar {class_name}" style="height: {height}px" title="{safe_text(label)}: {value}">{value}</div>'
        f'<div class="bar-label">{safe_text(symbol)} {safe_text(label)}</div>'
        "</div>"
    )


def render_status_chart(rows: pd.DataFrame, customers: list[str]) -> str:
    if rows.empty or not customers:
        chart_body = '<p class="muted-text" style="padding: 1rem;">No channels match the current filters.</p>'
    else:
        active_statuses = [status for status in STATUS_ORDER if status in set(rows["status"])]
        counts = []
        for customer in customers:
            customer_rows = rows[rows["portfolio"] == customer]
            status_counts = {
                status: int((customer_rows["status"] == status).sum())
                for status in active_statuses
            }
            counts.append({"portfolio": customer, **status_counts})

        if not active_statuses:
            chart_body = '<p class="muted-text" style="padding: 1rem;">No channel statuses match the active filters.</p>'
        else:
            max_count = max(
                1,
                max(max(item[status] for status in active_statuses) for item in counts),
            )
            chart_cards = []
            for item in counts:
                total = sum(item[status] for status in active_statuses)
                bars = "".join(
                    bar_markup(status.lower().replace(" ", "-"), status, item[status], max_count)
                    for status in active_statuses
                    if item[status] > 0
                )
                if not bars:
                    bars = '<span class="muted-text">No matching channels</span>'
                chart_cards.append(
                    f"""
                    <article class="portfolio-chart">
                      <div class="bar-stage" aria-label="{safe_text(item["portfolio"])} channel status counts">
                        {bars}
                      </div>
                      <div class="portfolio-label">
                        <span>{safe_text(item["portfolio"])}</span>
                        <span>{total} channels</span>
                      </div>
                      <div class="portfolio-footnote"><span>Filtered migration status</span></div>
                    </article>
                    """
                )
            chart_body = '<div class="chart-grid">' + "".join(chart_cards) + "</div>"

    return (
        '<section class="section-card">'
        + section_heading("Channels by Customer and Status", "LIVE, IN PROGRESS, and NEW channels")
        + chart_body
        + "</section>"
    )


def render_channel_table(rows: pd.DataFrame, customer_focus: str = "") -> str:
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

    detail = (
        f"{len(rows)} visible channels for {customer_focus}"
        if customer_focus
        else f"{len(rows)} visible channels"
    )
    return (
        '<section class="section-card">'
        + section_heading("Channel Status", detail)
        + '<div class="table-wrap"><table class="styled-table">'
        "<thead><tr>"
        "<th>Project</th><th>Channel</th><th>Status</th><th>Live / Proposed Go-Live</th><th>Notes</th>"
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
        icon = safe_text(str(row.chain)[:1].upper())
        cards.append(
            f"""
            <article class="upcoming-card">
              <div class="upcoming-top">
                <h3 class="upcoming-name"><span class="upcoming-icon">{icon}</span>{safe_text(row.chain)}</h3>
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


def slugify(value: object) -> str:
    text = str(value).lower()
    return "".join(char if char.isalnum() else "-" for char in text).strip("-")


def parse_date(value: object):
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def format_display_date(value: object) -> str:
    parsed = parse_date(value)
    return parsed.strftime("%Y-%m-%d") if parsed else ""


def compute_age_days(created_at: object, reference_date=None) -> int:
    reference = reference_date or CURRENT_VIEW_DATE.date()
    parsed = parse_date(created_at)
    if not parsed:
        return 0
    return max(0, (reference - parsed).days)


def compute_risk_score(record: dict) -> int:
    severity = SEVERITY_ORDER.get(str(record.get("severity", "None")), 0)
    age = int(record.get("age_days") or 0)
    escalated = 40 if bool(record.get("escalated")) else 0
    blocked = 25 if bool(record.get("blocked")) else 0
    missing_owner = 35 if not record.get("owner") and not record.get("accountable_owner") else 0
    return severity * 100 + age + escalated + blocked + missing_owner


def profile_for(customer: str) -> dict:
    return CUSTOMER_PROFILES.get(
        customer,
        {
            "accountable_owner": "Unassigned",
            "support_team": "Unassigned",
            "escalation_contact": "Unassigned",
            "next_milestone": "Confirm customer plan",
            "target_date": "",
        },
    )


def make_record(**kwargs) -> dict:
    record = {
        "record_id": "",
        "record_type": "",
        "customer": "",
        "project": "",
        "title": "",
        "description": "",
        "status": "Open",
        "severity": "None",
        "owner": "",
        "accountable_owner": "",
        "support_team": "",
        "escalation_contact": "",
        "source": "",
        "source_channel": "",
        "source_link": "",
        "created_at": CURRENT_VIEW_DATE.date().isoformat(),
        "updated_at": CURRENT_VIEW_DATE.date().isoformat(),
        "due_date": "",
        "age_days": 0,
        "health_state": "",
        "next_action": "",
        "impact": "",
        "blocked": False,
        "escalated": False,
        "duplicate_count": 1,
        "last_activity_at": CURRENT_VIEW_DATE.date().isoformat(),
        "escalation_status": "Not Escalated",
        "risk_score": 0,
    }
    record.update(kwargs)
    record["age_days"] = compute_age_days(record.get("created_at"))
    record["risk_score"] = compute_risk_score(record)
    if not record["record_id"]:
        record["record_id"] = (
            f"{record['record_type']}-{slugify(record['customer'])}-{slugify(record['title'])}"
        )
    return record


def normalize_source_records(
    channels: pd.DataFrame, issues: pd.DataFrame, manual_records: list[dict]
) -> pd.DataFrame:
    records: list[dict] = []

    for customer in sorted(channels["portfolio"].unique()):
        profile = profile_for(customer)
        records.append(
            make_record(
                record_type="customer",
                customer=customer,
                project=customer,
                title=f"{customer} operational ownership",
                description=profile["next_milestone"],
                status="Active",
                owner=profile["accountable_owner"],
                accountable_owner=profile["accountable_owner"],
                support_team=profile["support_team"],
                escalation_contact=profile["escalation_contact"],
                source="Customer profile",
                source_channel="Manual",
                due_date=profile["target_date"],
                health_state="Attention Needed",
                next_action=profile["next_milestone"],
                impact="Customer-level ownership and milestone tracking.",
            )
        )

    for _, issue in issues.iterrows():
        customer = issue["portfolio"]
        project = issue["project"]
        profile = profile_for(customer)
        defaults = {
            **profile,
            **ISSUE_ENRICHMENT.get((customer, project), {}),
        }
        severity = defaults.get("severity", "Medium")
        escalation_status = defaults.get("escalation_status", "In Progress")
        escalated = bool(defaults.get("escalated", escalation_status == "Escalated"))
        blocked = bool(defaults.get("blocked", severity in {"Critical", "High"}))
        created_at = defaults.get("created_at", CURRENT_VIEW_DATE.date().isoformat())
        source_channel = issue.get("link_type", "") or "Manual"
        source_link = issue.get("link", "")
        issue_record = make_record(
            record_type="issue",
            customer=customer,
            project=project,
            title=f"{project}: {issue['issue_type']}",
            description=issue["summary"],
            status="Open",
            severity=severity,
            owner=defaults.get("owner", defaults.get("accountable_owner", "")),
            accountable_owner=defaults.get("accountable_owner", profile["accountable_owner"]),
            support_team=defaults.get("support_team", profile["support_team"]),
            escalation_contact=defaults.get(
                "escalation_contact", profile["escalation_contact"]
            ),
            source=f"{source_channel} issue tracker",
            source_channel=source_channel,
            source_link=source_link,
            created_at=created_at,
            updated_at=defaults.get("updated_at", CURRENT_VIEW_DATE.date().isoformat()),
            due_date=defaults.get("due_date", ""),
            next_action=defaults.get("next_action", "Confirm owner, next action, and due date."),
            impact=defaults.get("impact", issue["summary"]),
            blocked=blocked,
            escalated=escalated,
            duplicate_count=1,
            last_activity_at=defaults.get("last_activity_at", created_at),
            escalation_status=escalation_status,
        )
        records.append(issue_record)

        if escalated or severity == "Critical":
            records.append(
                make_record(
                    **{
                        **issue_record,
                        "record_id": f"esc-{issue_record['record_id']}",
                        "record_type": "escalation",
                        "title": issue_record["title"],
                        "description": issue_record["description"],
                        "status": "Escalated",
                        "escalated": True,
                        "escalation_status": "Escalated",
                        "source": issue_record["source"],
                    }
                )
            )

    non_live = channels[channels["status"] != "LIVE"].copy()
    if not non_live.empty:
        for (customer, status), group in non_live.groupby(["portfolio", "status"]):
            profile = profile_for(customer)
            channel_names = ", ".join(group["channel"].head(4))
            if len(group) > 4:
                channel_names += f", +{len(group) - 4} more"
            delayed = group["notes"].str.contains("delayed|blocked|unable|pending", case=False, na=False).any()
            severity = "High" if delayed and status == "NEW" else "Medium"
            records.append(
                make_record(
                    record_type="risk_signal",
                    customer=customer,
                    project="Channel Status",
                    title=f"{len(group)} {status.title()} channel(s)",
                    description=f"{channel_names}: {status.title()} status requires active follow-up.",
                    status=status,
                    severity=severity,
                    owner=profile["accountable_owner"],
                    accountable_owner=profile["accountable_owner"],
                    support_team=profile["support_team"],
                    escalation_contact=profile["escalation_contact"],
                    source="Channel status table",
                    source_channel="Manual",
                    created_at=CURRENT_VIEW_DATE.date().isoformat(),
                    updated_at=CURRENT_VIEW_DATE.date().isoformat(),
                    due_date=profile["target_date"],
                    next_action="Confirm owner progress and next milestone for grouped channels.",
                    impact=f"{len(group)} channel(s) not yet live.",
                    blocked=status == "NEW",
                    escalated=False,
                    duplicate_count=int(len(group)),
                    last_activity_at=CURRENT_VIEW_DATE.date().isoformat(),
                    escalation_status="Watch" if status == "NEW" else "Not Escalated",
                )
            )

    for manual in manual_records:
        records.append(make_record(**manual))

    return pd.DataFrame(records)


def compute_customer_health(customer: str, channels: pd.DataFrame, records: pd.DataFrame) -> dict:
    customer_channels = channels[channels["portfolio"] == customer]
    customer_records = records[
        (records["customer"] == customer) & (records["record_type"] != "customer")
    ]
    live_count = int((customer_channels["status"] == "LIVE").sum())
    in_progress_count = int((customer_channels["status"] == "IN PROGRESS").sum())
    new_count = int((customer_channels["status"] == "NEW").sum())
    blocked_records = int(customer_records["blocked"].fillna(False).sum()) if not customer_records.empty else 0
    blocked_count = new_count + blocked_records
    escalated = bool(customer_records["escalated"].fillna(False).any()) if not customer_records.empty else False
    critical = bool((customer_records["severity"] == "Critical").any()) if not customer_records.empty else False
    high = bool((customer_records["severity"] == "High").any()) if not customer_records.empty else False

    if escalated or critical:
        health_state = "Escalated"
    elif blocked_count > 0 or high:
        health_state = "At Risk"
    elif in_progress_count > 0 or not customer_records.empty:
        health_state = "Attention Needed"
    else:
        health_state = "Healthy"

    profile = profile_for(customer)
    top_record = (
        customer_records.sort_values(["risk_score", "age_days"], ascending=False).head(1)
        if not customer_records.empty
        else pd.DataFrame()
    )
    next_action = (
        top_record.iloc[0]["next_action"] if not top_record.empty else profile["next_milestone"]
    )
    target_date = (
        top_record.iloc[0]["due_date"]
        if not top_record.empty and top_record.iloc[0]["due_date"]
        else profile["target_date"]
    )
    total = int(len(customer_channels))
    completion = live_count / total if total else 0
    return {
        "customer": customer,
        "health_state": health_state,
        "live_count": live_count,
        "in_progress_count": in_progress_count,
        "blocked_count": blocked_count,
        "total_channels": total,
        "completion": completion,
        "next_milestone": profile["next_milestone"],
        "target_date": target_date,
        "owner": profile["accountable_owner"],
        "accountable_owner": profile["accountable_owner"],
        "support_team": profile["support_team"],
        "escalation_contact": profile["escalation_contact"],
        "next_action": next_action,
        "last_updated": CURRENT_VIEW_DATE.strftime("%Y-%m-%d %H:%M"),
        "open_items": int(len(customer_records)),
        "missing_owner_count": int(
            customer_records["owner"].fillna("").eq("").sum()
        )
        if not customer_records.empty
        else 0,
    }


def aggregate_customer_rollups(channels: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
    rows = [
        compute_customer_health(customer, channels, records)
        for customer in sorted(channels["portfolio"].unique())
    ]
    return pd.DataFrame(rows).sort_values(
        "health_state", key=lambda values: values.map(HEALTH_ORDER), ascending=False
    )


def aggregate_escalations(records: pd.DataFrame) -> pd.DataFrame:
    if records.empty:
        return records
    escalations = records[records["record_type"] == "escalation"].copy()
    if escalations.empty:
        return escalations
    return escalations.sort_values(["risk_score", "age_days"], ascending=False)


def severity_badge(severity: object) -> str:
    value = safe_text(severity or "None")
    css = f"severity-{value.lower()}"
    symbol = SEVERITY_SYMBOLS.get(value, "•")
    return (
        f'<span class="status-badge {css}">'
        f'<span class="badge-symbol">{safe_text(symbol)}</span>{value}</span>'
    )


def health_badge(health: object) -> str:
    value = safe_text(health)
    css = f"health-{value.lower().replace(' ', '-')}"
    symbol = HEALTH_SYMBOLS.get(value, "•")
    return (
        f'<span class="status-badge {css}">'
        f'<span class="badge-symbol">{safe_text(symbol)}</span>{value}</span>'
    )


def owner_cell(owner: object) -> str:
    text = safe_text(owner)
    if not text or text == "Unassigned":
        return '<span class="owner-missing">Missing owner</span>'
    return text


def render_source_cell(row: pd.Series) -> str:
    label = safe_text(row.get("source_channel", "") or row.get("source", ""))
    link = row.get("source_link", "")
    if link:
        return render_link(link, label or "Open source")
    return label or '<span class="muted-text">Manual</span>'


def render_customer_health(rows: pd.DataFrame) -> str:
    if rows.empty:
        body = '<p class="muted-text" style="padding:1rem;">No customers match the active filters.</p>'
    else:
        cards = []
        for row in rows.itertuples(index=False):
            health_class = f"health-{row.health_state.lower().replace(' ', '-')}"
            percent = int(round(float(row.completion) * 100))
            cards.append(
                f"""
                <article class="health-card {health_class}">
                  <div class="health-top">
                    <h3>{safe_text(row.customer)}</h3>
                    {health_badge(row.health_state)}
                  </div>
                  <div class="health-counts">
                    <span class="mini-stat"><strong>{int(row.live_count)}</strong><span>Live</span></span>
                    <span class="mini-stat"><strong>{int(row.in_progress_count)}</strong><span>In progress</span></span>
                    <span class="mini-stat"><strong>{int(row.blocked_count)}</strong><span>Blocked</span></span>
                  </div>
                  <div class="progress-track" aria-label="{safe_text(row.customer)} completion">
                    <div class="progress-fill" style="width:{percent}%"></div>
                  </div>
                  <p class="health-detail"><strong>Milestone:</strong> {safe_text(row.next_milestone)}</p>
                  <p class="health-detail"><strong>Target:</strong> {safe_text(row.target_date)} | <strong>Owner:</strong> {owner_cell(row.owner)}</p>
                  <p class="health-meta">Updated {safe_text(row.last_updated)} | {percent}% live</p>
                </article>
                """
            )
        body = '<div class="health-grid">' + "".join(cards) + "</div>"
    return (
        '<section class="section-card">'
        + section_heading("Customer Health", "Ownership, milestones, blockers")
        + body
        + "</section>"
    )


def render_ownership_matrix(rows: pd.DataFrame) -> str:
    if rows.empty:
        body = '<tr><td colspan="7" class="muted-text">No ownership rows match filters.</td></tr>'
    else:
        body = "".join(
            f"""
            <tr>
              <td>{safe_text(row.customer)}</td>
              <td>{health_badge(row.health_state)}</td>
              <td>{owner_cell(row.accountable_owner)}</td>
              <td>{safe_text(row.support_team)}</td>
              <td>{safe_text(row.escalation_contact)}</td>
              <td>{int(row.open_items)}</td>
              <td>{int(row.missing_owner_count)}</td>
            </tr>
            """
            for row in rows.itertuples(index=False)
        )
    return (
        '<section class="section-card">'
        + section_heading("Ownership Matrix", "Accountable owner, support team, escalation path")
        + '<div class="table-wrap"><table class="styled-table"><thead><tr>'
        '<th>Customer</th><th>Health</th><th>Accountable Owner</th><th>Supporting Team</th><th>Escalation Contact</th><th>Open Items</th><th>Missing Owner</th>'
        '</tr></thead><tbody>'
        + body
        + "</tbody></table></div></section>"
    )


def render_open_issues(rows: pd.DataFrame, customer_focus: str = "") -> str:
    if rows.empty:
        body = '<tr><td colspan="9" class="muted-text">No open issues or blockers match filters.</td></tr>'
        critical_note = ""
    else:
        critical_count = int(
            ((rows["severity"] == "Critical") | (rows["escalation_status"] == "Escalated")).sum()
        )
        critical_note = (
            f'<div class="attention-strip">{critical_count} critical or escalated item(s) require executive attention.</div>'
            if critical_count
            else ""
        )
        body = "".join(
            f"""
            <tr>
              <td>{severity_badge(row["severity"])}</td>
              <td>{safe_text(row["customer"])}</td>
              <td>{safe_text(row["title"])}</td>
              <td>{owner_cell(row["owner"])}</td>
              <td>{int(row["age_days"])}</td>
              <td>{safe_text(row["impact"])}</td>
              <td>{safe_text(row["escalation_status"])}</td>
              <td>{safe_text(row["next_action"])}</td>
              <td>{render_source_cell(row)}</td>
            </tr>
            """
            for _, row in rows.iterrows()
        )
    detail = (
        f"{len(rows)} prioritized issue(s) for {customer_focus}"
        if customer_focus
        else f"{len(rows)} prioritized issue(s)"
    )
    return (
        '<section class="section-card">'
        + section_heading("Issue Tracker", detail)
        + critical_note
        + '<div class="table-wrap"><table class="styled-table"><thead><tr>'
        '<th>Severity</th><th>Customer</th><th>Issue</th><th>Owner</th><th>Age</th><th>Impact</th><th>Escalation</th><th>Next Action</th><th>Source</th>'
        '</tr></thead><tbody>'
        + body
        + "</tbody></table></div></section>"
    )


def render_escalations(rows: pd.DataFrame) -> str:
    if rows.empty:
        body = '<tr><td colspan="6" class="muted-text">No active executive escalations match filters.</td></tr>'
    else:
        body = "".join(
            f"""
            <tr>
              <td>{safe_text(row["title"])}</td>
              <td>{safe_text(row["created_at"])}</td>
              <td>{owner_cell(row["owner"])}</td>
              <td>{severity_badge(row["severity"])}</td>
              <td>{safe_text(row["next_action"])}</td>
              <td>{safe_text(row["due_date"])}</td>
            </tr>
            """
            for _, row in rows.iterrows()
        )
    return (
        '<section class="section-card">'
        + section_heading("Executive Escalations", "Triggers, owners, due dates")
        + '<div class="table-wrap"><table class="styled-table"><thead><tr>'
        '<th>Trigger</th><th>Triggered</th><th>Owner</th><th>Severity</th><th>Next Action</th><th>Due Date</th>'
        '</tr></thead><tbody>'
        + body
        + "</tbody></table></div></section>"
    )


def render_risk_feed(rows: pd.DataFrame) -> str:
    if rows.empty:
        body = '<tr><td colspan="8" class="muted-text">No risk signals match filters.</td></tr>'
    else:
        body = "".join(
            f"""
            <tr>
              <td>{safe_text(row["customer"])}</td>
              <td>{safe_text(row["description"])}</td>
              <td>{safe_text(row["source_channel"])}</td>
              <td>{severity_badge(row["severity"])}</td>
              <td>{owner_cell(row["owner"])}</td>
              <td>{safe_text(row["project"])}</td>
              <td>{safe_text(row["last_activity_at"])}</td>
              <td>{int(row["duplicate_count"])}</td>
            </tr>
            """
            for _, row in rows.iterrows()
        )
    return (
        '<section class="section-card">'
        + section_heading("Risk Feed", "Slack, Jira, manual, and channel-status signals")
        + '<div class="table-wrap"><table class="styled-table"><thead><tr>'
        '<th>Customer</th><th>Signal Summary</th><th>Source Channel</th><th>Severity</th><th>Owner</th><th>Linked Item</th><th>Timestamp</th><th>Mentions</th>'
        '</tr></thead><tbody>'
        + body
        + "</tbody></table></div></section>"
    )


# ----------------------------
# Executive command center
# ----------------------------

if "manual_records" not in st.session_state:
    st.session_state["manual_records"] = []

records_df = normalize_source_records(
    df_channels, df_issues, st.session_state["manual_records"]
)
health_df = aggregate_customer_rollups(df_channels, records_df)

customer_options = sorted(df_channels["portfolio"].unique())
status_options = [status for status in STATUS_ORDER if status in set(df_channels["status"])]
severity_options = [
    severity
    for severity in ["Critical", "High", "Medium", "Low", "None"]
    if severity in set(records_df["severity"])
]
owner_options = sorted(
    {
        owner
        for owner in records_df["owner"].fillna("").tolist()
        + records_df["accountable_owner"].fillna("").tolist()
        if owner
    }
)
escalation_options = sorted(
    status for status in records_df["escalation_status"].fillna("").unique() if status
)
source_channel_options = sorted(
    channel for channel in records_df["source_channel"].fillna("").unique() if channel
)
health_options = [
    health
    for health in ["Escalated", "At Risk", "Attention Needed", "Healthy"]
    if health in set(health_df["health_state"])
]

focused_customer = query_customer(customer_options)
selected_customers = [focused_customer] if focused_customer else customer_options
selected_statuses = status_options
selected_severities = severity_options
selected_owners = owner_options
selected_escalations = escalation_options
selected_source_channels = source_channel_options
selected_health_states = health_options
search_text = ""

customer_scope_channels = df_channels[df_channels["portfolio"].isin(selected_customers)].copy()
customer_scope_records = records_df[records_df["customer"].isin(selected_customers)].copy()

filtered_records = customer_scope_records[
    customer_scope_records["severity"].isin(selected_severities)
    & customer_scope_records["escalation_status"].isin(selected_escalations)
    & customer_scope_records["source_channel"].isin(selected_source_channels)
    & (
        customer_scope_records["owner"].isin(selected_owners)
        | customer_scope_records["accountable_owner"].isin(selected_owners)
    )
].copy()

if search_text:
    record_search = (
        filtered_records["customer"].str.contains(search_text, case=False, na=False)
        | filtered_records["project"].str.contains(search_text, case=False, na=False)
        | filtered_records["title"].str.contains(search_text, case=False, na=False)
        | filtered_records["description"].str.contains(search_text, case=False, na=False)
        | filtered_records["impact"].str.contains(search_text, case=False, na=False)
        | filtered_records["next_action"].str.contains(search_text, case=False, na=False)
    )
    filtered_records = filtered_records[record_search]

health_view = health_df[
    health_df["customer"].isin(selected_customers)
    & health_df["health_state"].isin(selected_health_states)
].copy()
if selected_owners:
    health_view = health_view[health_view["accountable_owner"].isin(selected_owners)]
if search_text:
    health_view = health_view[
        health_view["customer"].str.contains(search_text, case=False, na=False)
        | health_view["next_milestone"].str.contains(search_text, case=False, na=False)
        | health_view["next_action"].str.contains(search_text, case=False, na=False)
    ]

filtered_channels = customer_scope_channels[
    customer_scope_channels["status"].isin(selected_statuses)
].copy()
if search_text:
    channel_search = (
        filtered_channels["channel"].str.contains(search_text, case=False, na=False)
        | filtered_channels["portfolio"].str.contains(search_text, case=False, na=False)
        | filtered_channels["project"].str.contains(search_text, case=False, na=False)
        | filtered_channels["notes"].str.contains(search_text, case=False, na=False)
    )
    filtered_channels = filtered_channels[channel_search]

overview_customers = [
    customer
    for customer in selected_customers
    if customer in set(customer_scope_channels["portfolio"])
]
completion_rows = build_completion_rows(df_channels)

open_operational_records = filtered_records[
    filtered_records["record_type"].isin(["issue", "risk_signal", "escalation"])
].copy()
open_issues = open_operational_records[
    open_operational_records["record_type"].isin(["issue", "risk_signal"])
].sort_values(["risk_score", "age_days"], ascending=False)
escalations = aggregate_escalations(filtered_records)
risk_feed = filtered_records[
    filtered_records["record_type"].isin(["risk_signal", "issue", "escalation"])
].sort_values(["risk_score", "age_days"], ascending=False)

missing_owner_count = int(
    open_operational_records["owner"].fillna("").eq("").sum()
    + open_operational_records["accountable_owner"].fillna("").eq("").sum()
)

st.html(render_completion_cards(completion_rows, health_df, records_df, focused_customer))
st.html(render_status_chart(filtered_channels, overview_customers))

if missing_owner_count:
    st.warning(
        f"{missing_owner_count} operational ownership field(s) are missing. Assign an owner before executive review."
    )

st.html(render_open_issues(open_issues, focused_customer))

# ----------------------------
# Detailed channel table
# ----------------------------

channels_display = filtered_channels.copy()
channels_display["project"] = channels_display["portfolio"]
channels_display["go_live_date"] = channels_display["go_live_date"].apply(
    lambda value: value.strftime("%Y-%m-%d") if pd.notna(value) else ""
)
channels_display = channels_display[["project", "channel", "status", "go_live_date", "notes"]]
channels_display = channels_display.rename(
    columns={
        "project": "Project",
        "channel": "Channel",
        "status": "Status",
        "go_live_date": "Live / Proposed Go-Live",
        "notes": "Notes",
    }
)

st.html(render_channel_table(channels_display, focused_customer))
st.html(render_upcoming_cards(df_upcoming_chains))

download_channels = df_channels.copy()
download_channels["project"] = download_channels["portfolio"]
download_channels = download_channels[["project", "channel", "status", "go_live_date", "notes"]]
csv = download_channels.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download channel data as CSV",
    data=csv,
    file_name="channel_status_data.csv",
    mime="text/csv",
)

st.caption("Executive operational view generated from normalized customer, issue, escalation, risk, and channel records.")
