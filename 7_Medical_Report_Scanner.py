import pandas as pd
import plotly.express as px
import streamlit as st

from auth.auth_manager import require_login
from database import db_manager
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
    render_stat_cards,
)

set_page("Pregnancy History", "📈")
user = require_login()
render_navbar(active="Pregnancy History")
render_user_bar(user)

section_header(
    "Your records",
    "Pregnancy History",
    "Every risk prediction you've run is automatically logged here — "
    "search, filter, and export it any time.",
)

PRIMARY = "#FF4F9A"
ACCENT = "#A855F7"
CHART_COLORS = {"Low": "#22C55E", "Moderate": "#F59E0B", "High": "#EF4444"}

# -----------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------
records = db_manager.get_predictions(user["id"])

if not records:
    with st.container(key="glass_hist_empty"):
        st.info(
            "You don't have any saved predictions yet. Run a risk "
            "prediction and it will automatically show up here."
        )
        st.page_link("pages/1_Risk_Prediction.py", label="Go to Risk Prediction →")
    render_footer()
    st.stop()

df = pd.DataFrame(records)
df["created_at"] = pd.to_datetime(df["created_at"])
df = df.sort_values("created_at", ascending=False)

# -----------------------------------------------------------------------
# Statistics
# -----------------------------------------------------------------------
stats = db_manager.get_prediction_stats(user["id"])

with st.container(key="glass_hist_overview"):
    st.markdown("#### 📊 Overview")
    render_stat_cards([
        ("🧾", "Total Predictions", str(stats["count"])),
        ("💓", "Avg. Systolic BP", f"{stats['avg_systolic']} mmHg"),
        ("💉", "Avg. Diastolic BP", f"{stats['avg_diastolic']} mmHg"),
        ("🍬", "Avg. Blood Sugar", f"{stats['avg_glucose']} mg/dL"),
    ])

chart_l, chart_r = st.columns(2)
with chart_l:
    with st.container(key="glass_hist_pie"):
        st.markdown("##### Risk Level Distribution")
        dist = stats["risk_distribution"]
        dist_df = pd.DataFrame(
            {"Risk Level": list(dist.keys()), "Count": list(dist.values())}
        )
        fig_pie = px.pie(
            dist_df,
            names="Risk Level",
            values="Count",
            color="Risk Level",
            color_discrete_map=CHART_COLORS,
            hole=0.55,
        )
        fig_pie.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with chart_r:
    with st.container(key="glass_hist_line"):
        st.markdown("##### Blood Pressure Over Time")
        bp_df = df.sort_values("created_at")
        fig_line = px.line(
            bp_df,
            x="created_at",
            y=["systolic_bp", "diastolic_bp"],
            labels={"created_at": "Date", "value": "mmHg", "variable": "Reading"},
            color_discrete_sequence=[PRIMARY, ACCENT],
            markers=True,
        )
        fig_line.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_line, use_container_width=True)

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Search & filters
# -----------------------------------------------------------------------
with st.container(key="glass_hist_filters"):
    st.markdown("#### 🔍 Search & Filter")
    f1, f2, f3 = st.columns([1.4, 1, 1])
    with f1:
        search_term = st.text_input(
            "Search", placeholder="Search by risk level or date…"
        )
    with f2:
        risk_options = ["All"] + sorted(df["risk_level"].dropna().unique().tolist())
        risk_filter = st.selectbox("Filter by Risk Level", risk_options)
    with f3:
        date_filter = st.date_input(
            "Filter by Date", value=None, format="YYYY-MM-DD"
        )

filtered = df.copy()
if search_term:
    mask = (
        filtered["predicted_risk"].astype(str).str.contains(search_term, case=False, na=False)
        | filtered["risk_level"].astype(str).str.contains(search_term, case=False, na=False)
        | filtered["created_at"].astype(str).str.contains(search_term, case=False, na=False)
    )
    filtered = filtered[mask]
if risk_filter != "All":
    filtered = filtered[filtered["risk_level"] == risk_filter]
if date_filter:
    filtered = filtered[filtered["created_at"].dt.date == date_filter]

# -----------------------------------------------------------------------
# Sortable table
# -----------------------------------------------------------------------
with st.container(key="glass_hist_table"):
    st.markdown(f"#### 🗂️ Records ({len(filtered)})")

    sort_col, sort_dir = st.columns([2, 1])
    with sort_col:
        sortable_columns = {
            "Date (newest first)": ("created_at", False),
            "Date (oldest first)": ("created_at", True),
            "Age": ("age", True),
            "Systolic BP": ("systolic_bp", True),
            "Blood Sugar": ("blood_sugar", True),
        }
        sort_choice = st.selectbox("Sort by", list(sortable_columns.keys()))
    sort_field, ascending = sortable_columns[sort_choice]
    filtered = filtered.sort_values(sort_field, ascending=ascending)

    display_df = filtered.rename(
        columns={
            "created_at": "Date & Time",
            "age": "Age",
            "systolic_bp": "Systolic BP",
            "diastolic_bp": "Diastolic BP",
            "blood_sugar": "Blood Sugar",
            "body_temperature": "Body Temp (°C)",
            "heart_rate": "Heart Rate",
            "predicted_risk": "Predicted Risk",
            "recommendation": "AI Recommendation",
        }
    )[
        [
            "Date & Time", "Age", "Systolic BP", "Diastolic BP", "Blood Sugar",
            "Body Temp (°C)", "Heart Rate", "Predicted Risk", "AI Recommendation",
        ]
    ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # Export
    # -------------------------------------------------------------
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export to CSV",
        data=csv_bytes,
        file_name=f"pregnancy_history_{user['id']}.csv",
        mime="text/csv",
        use_container_width=False,
    )

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Delete records
# -----------------------------------------------------------------------
with st.container(key="glass_hist_delete"):
    st.markdown("#### 🗑️ Delete a Record")
    st.caption("Select a record by its date & time to permanently remove it.")

    options = {
        f"{row['created_at']} — {row['predicted_risk']}": row["id"]
        for _, row in filtered.iterrows()
    }
    if options:
        del_col, btn_col = st.columns([3, 1])
        with del_col:
            choice = st.selectbox("Record", list(options.keys()), label_visibility="collapsed")
        with btn_col:
            if st.button("Delete", use_container_width=True):
                db_manager.delete_prediction(options[choice], user["id"])
                st.success("Record deleted.")
                st.rerun()
    else:
        st.write("No records match the current filters.")

render_footer()
