from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Chain Status Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Chain Status Dashboard")
st.caption("Implementation projects, channel go-live status, and active issue tracking.")

BASE_DIR = Path(__file__).parent
LOGO_PATHS = {
    "Great Wolf": BASE_DIR / "assets" / "great-wolf.svg",
    "Loews": BASE_DIR / "assets" / "loews.svg",
    "Pan Pacific": BASE_DIR / "assets" / "pan-pacific.svg",
}

# ----------------------------
# Source data
# ----------------------------

channels_data = [
    # Great Wolf
    {"portfolio": "Great Wolf", "project": "IBE", "channel": "IBE", "status": "LIVE", "go_live_date": "2026-04-15", "notes": "Finalized and handed over to Support."},
    {"portfolio": "Great Wolf", "project": "Groupon", "channel": "Groupon", "status": "LIVE", "go_live_date": "2026-05-07", "notes": "All batches migrated; stabilization in progress."},
    {"portfolio": "Great Wolf", "project": "Expedia", "channel": "Expedia", "status": "LIVE", "go_live_date": "2026-05-07", "notes": "Pilot + batches 1-3 are live. Remaining properties on pause due to extra person rate issue, under review."},
    {"portfolio": "Great Wolf", "project": "HGV", "channel": "HGV", "status": "NEW", "go_live_date": "", "notes": "Connectivity development finalized; partner delays remain."},
    {"portfolio": "Great Wolf", "project": "Google via DerbySoft Meta", "channel": "Google / DerbySoft Meta", "status": "NEW", "go_live_date": "", "notes": "Validation in progress by DerbySoft."},
    {"portfolio": "Great Wolf", "project": "Booking.com for NIAGON", "channel": "Booking.com for NIAGON", "status": "NEW", "go_live_date": "2026-06-01", "notes": "Separate onboarding track; go-live scheduled."},
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
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "WebBeds - Sunhotels", "status": "LIVE", "go_live_date": "2026-03-13", "notes": "Activated with switch partner (13-Mar-26 - PPYGN, 17-Mar-26 - PPDAC, 26-Mar-26 - remaining hotels); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Luxury Escapes", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); OTA Test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Flight Centre Travel", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Ly.com", "status": "LIVE", "go_live_date": "2026-05-21", "notes": "Activated with switch partner (21 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Hotelbeds", "status": "LIVE", "go_live_date": "2026-03-11", "notes": "Activated with switch partner (11-Mar-26 - PPYGN, 20-Apr-26 - remaining hotels); OTA test booking confirmed, handed over to support"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Tiket", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Activated with switch partner (20 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Tidesquare", "status": "LIVE", "go_live_date": "2026-05-19", "notes": "Activated with switch partner (19 May); pending OTA test booking"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Klook", "status": "LIVE", "go_live_date": "2026-05-20", "notes": "Activated with switch partner (20 May); pending OTA test booking. Excl. PRLGK, pending room type mapping from PPHG"},
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
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "MG Bedbank", "status": "NEW", "go_live_date": "", "notes": "Pilot property (PRYGN) activated with switch partner (26 May), pending OTA confirmation before proceeding with remaining hotels"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Agoda", "status": "NEW", "go_live_date": "", "notes": "Configuration with OTA underway"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Trip.com", "status": "NEW", "go_live_date": "", "notes": "Conversations ongoing between Trip and PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Roibos", "status": "NEW", "go_live_date": "", "notes": "Roibos in contact with PPHG regarding contractual details, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Goibibo & MakeMyTrip", "status": "NEW", "go_live_date": "", "notes": "Ongoing configuration work required at OTA end, unable to onboard this channel currently"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Emerging Travel", "status": "NEW", "go_live_date": "", "notes": "Awaiting confirmation from OTA to proceed"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Nuitee", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Inntopia", "status": "NEW", "go_live_date": "", "notes": "PPHG advised channel will not be part of this batch."},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Rakuten", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "Travco", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG"},
    {"portfolio": "Pan Pacific", "project": "Pan Pacific", "channel": "TA Network", "status": "NEW", "go_live_date": "", "notes": "Pending OTA engagement and mapping from PPHG"},
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
        "portfolio": "Loews",
        "project": "Booking.com",
        "issue_type": "Operational issue",
        "link_type": "JIRA",
        "link": "https://jira.example.com/browse/LOEWS-BOOKING-001",
        "summary": "Reservations are not consistently interfacing into OPERA; email/contact configuration and reservation notes are being investigated.",
    },
    {
        "portfolio": "Loews",
        "project": "GDS",
        "issue_type": "JIRA",
        "link_type": "JIRA",
        "link": "https://jira.example.com/browse/260515-001045",
        "summary": "Free night promotions on rate codes are not displaying or pricing correctly in GDS/Sabre.",
    },
    {
        "portfolio": "Loews",
        "project": "GDS",
        "issue_type": "JIRA",
        "link_type": "JIRA",
        "link": "https://jira.example.com/browse/260512-001287",
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

# ----------------------------
# Project completion tracker
# ----------------------------

st.subheader("Project Completion")
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

completion_cards = st.columns(len(completion_rows))
for card, row in zip(completion_cards, completion_rows.itertuples(index=False)):
    with card:
        logo_path = LOGO_PATHS.get(row.portfolio)
        if logo_path and logo_path.exists():
            st.image(str(logo_path), width=90)
        percent = float(row.completion)
        st.markdown(f"**{row.portfolio}**")
        st.progress(percent, text=f"{percent:.0%} complete")
        st.caption(
            f"{row.live_channels} of {row.total_channels} LIVE | "
            f"{row.total_channels - row.live_channels} remaining"
        )

st.divider()

# ----------------------------
# Filters
# ----------------------------

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
# Top visual
# ----------------------------

status_counts = (
    filtered_channels.groupby(["portfolio", "status"], as_index=False)
    .size()
    .rename(columns={"size": "count"})
)

fig = px.bar(
    status_counts,
    x="portfolio",
    y="count",
    color="status",
    barmode="group",
    text="count",
    title="Channels by Customer and Status",
)
fig.update_layout(
    xaxis_title="Customer",
    yaxis_title="Channel Count",
    legend_title_text="Status",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Channels table
# ----------------------------

st.subheader("Channel Status")
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

st.dataframe(
    channels_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Project": st.column_config.TextColumn(width="large"),
        "Channel": st.column_config.TextColumn(width="large"),
        "Status": st.column_config.TextColumn(width="small"),
        "Live / Proposed Go-Live": st.column_config.TextColumn(width="medium"),
        "Notes": st.column_config.TextColumn(width="large"),
    },
)

# ----------------------------
# Issue tracker
# ----------------------------

st.subheader("Issue Tracker")

issues_display = df_issues.copy()
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

st.data_editor(
    issues_display,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "Customer": st.column_config.SelectboxColumn(
            "Customer",
            options=["Great Wolf", "Loews", "Pan Pacific"],
        ),
        "Project": st.column_config.TextColumn(width="large"),
        "Issue Type": st.column_config.TextColumn(width="medium"),
        "Link Type": st.column_config.SelectboxColumn(
            "Link Type",
            options=["Slack", "JIRA", "Other"],
        ),
        "Slack / JIRA Link": st.column_config.LinkColumn(
            "Slack / JIRA Link",
            display_text="Open link",
        ),
        "Summary": st.column_config.TextColumn(width="large"),
    },
)

# ----------------------------
# Upcoming chain migrations
# ----------------------------

st.subheader("Upcoming Chain Migrations")
upcoming_display = df_upcoming_chains.rename(
    columns={
        "chain": "Chain",
        "hotels": "Hotels",
        "go_live": "Go Live",
        "channels": "Channels",
        "slack": "Slack",
    }
)

st.dataframe(
    upcoming_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Chain": st.column_config.TextColumn(width="medium"),
        "Hotels": st.column_config.TextColumn(width="small"),
        "Go Live": st.column_config.TextColumn(width="medium"),
        "Channels": st.column_config.TextColumn(width="large"),
        "Slack": st.column_config.LinkColumn("Slack", display_text="Open Slack"),
    },
)

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
