from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "ailean_logo.png"

from src.charts import (
    downtime_pareto,
    loss_by_shift,
    oee_by_machine,
    oee_loss_tree,
    oee_trend,
    production_by_line,
    quality_heatmap,
    risk_by_machine,
)
from src.data import apply_filters, load_operations_data
from src.insights import build_action_recommendations, format_pct
from src.kpis import add_oee_columns, calculate_kpis
from src.styles import inject_css



def get_image_base64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


st.set_page_config(
    page_title="AILean Factory Intelligence Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

raw_df = load_operations_data()
df = add_oee_columns(raw_df)

st.sidebar.image(str(LOGO_PATH), width=190)
st.sidebar.markdown('<div class="sidebar-brand">AILean Consulting</div>', unsafe_allow_html=True)
st.sidebar.title("🏭 Plant Filters")
st.sidebar.caption("Use these filters to isolate a plant, line, machine, shift, or product family.")

min_date = pd.to_datetime(df["date"]).min().date()
max_date = pd.to_datetime(df["date"]).max().date()
date_range = st.sidebar.date_input("Production date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    selected_date_range = (pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]))
else:
    selected_date_range = (pd.Timestamp(min_date), pd.Timestamp(max_date))

plants = st.sidebar.multiselect("Plant", sorted(df["plant_id"].dropna().unique()))
lines = st.sidebar.multiselect("Line", sorted(df["line_id"].dropna().unique()))
machines = st.sidebar.multiselect("Machine", sorted(df["machine_id"].dropna().unique()))
shifts = st.sidebar.multiselect("Shift", sorted(df["shift"].dropna().unique()))
products = st.sidebar.multiselect("Product", sorted(df["product_id"].dropna().unique()))

filtered_df = apply_filters(df, plants, lines, machines, shifts, products, selected_date_range)

logo_base64 = get_image_base64(LOGO_PATH)
st.markdown(
    f"""
<div class="hero">
  <div class="hero-brand-row">
    <img src="data:image/png;base64,{logo_base64}" class="hero-logo" alt="AILean logo" />
    <div class="hero-brand-copy">
      <div class="hero-topline">
        <span class="eyebrow">AILean Consulting</span>
        <span class="hero-pill">OEE • Downtime • Quality • Risk</span>
      </div>
      <h1>AILean Factory Intelligence Dashboard</h1>
      <p>Practical AI for OEE, downtime, quality, and production loss improvement.</p>
      <p class="hero-subtext">See where production is being lost, which machines need attention, where quality is slipping, and what the plant team should do next.</p>
    </div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.warning("No manufacturing records match the selected filters. Broaden the filters to continue.")
    st.stop()

kpis = calculate_kpis(filtered_df)

metric_cols = st.columns(6)
metric_data = [
    ("OEE", format_pct(kpis["oee"]), "Availability × Performance × Quality"),
    ("Availability", format_pct(kpis["availability"]), "Runtime vs planned production time"),
    ("Performance", format_pct(kpis["performance"]), "Actual output vs target output"),
    ("Quality", format_pct(kpis["quality"]), "Good units vs total produced"),
    ("Downtime", f"{kpis['downtime_min']:,.0f} min", "Total lost production minutes"),
    ("Estimated Loss", f"${kpis['estimated_loss_value']:,.0f}", "Output loss converted to value"),
]

for col, (label, value, help_text) in zip(metric_cols, metric_data):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{value}</div>
              <div class="metric-help">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<h3 class="section-title">OEE & Production Loss</h3>', unsafe_allow_html=True)
left, right = st.columns([1.15, 1])
with left:
    st.plotly_chart(oee_trend(filtered_df), use_container_width=True)
with right:
    st.plotly_chart(oee_by_machine(filtered_df), use_container_width=True)

left, right = st.columns([1, 1])
with left:
    st.plotly_chart(oee_loss_tree(filtered_df), use_container_width=True)
with right:
    st.plotly_chart(production_by_line(filtered_df), use_container_width=True)

st.markdown('<h3 class="section-title">Downtime, Quality & Maintenance Risk</h3>', unsafe_allow_html=True)
col1, col2 = st.columns([1.1, 0.9])
with col1:
    st.plotly_chart(downtime_pareto(filtered_df), use_container_width=True)
with col2:
    st.plotly_chart(loss_by_shift(filtered_df), use_container_width=True)

col3, col4 = st.columns([1.05, 0.95])
with col3:
    st.plotly_chart(quality_heatmap(filtered_df), use_container_width=True)
with col4:
    st.plotly_chart(risk_by_machine(filtered_df), use_container_width=True)

summary_cols = st.columns(4)
summary_cards = [
    ("Worst Machine", kpis["worst_machine"], "Highest downtime contributor"),
    ("Top Loss Reason", kpis["top_loss_reason"], "Primary downtime category"),
    ("MTTR", f"{kpis['mttr']:.1f} min", "Mean time to repair"),
    ("MTBF", f"{kpis['mtbf']:.1f} min", "Mean time between failures"),
]
for col, (label, value, help_text) in zip(summary_cols, summary_cards):
    with col:
        st.markdown(
            f"""
            <div class="metric-card compact-metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value compact-metric-value">{value}</div>
              <div class="metric-help">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<h3 class="section-title action-section-title">Plant Manager Action Center</h3>', unsafe_allow_html=True)
actions = build_action_recommendations(filtered_df, kpis)
action_cols = st.columns(2)
for i, action in enumerate(actions):
    with action_cols[i % 2]:
        st.markdown(
            f"""
            <div class="action-card">
                <div class="action-title">{action['title']}</div>
                <div class="action-body">{action['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


with st.expander("View filtered manufacturing records"):
    display_cols = [
        "date",
        "plant_id",
        "line_id",
        "machine_id",
        "shift",
        "product_id",
        "planned_production_time_min",
        "runtime_min",
        "downtime_min",
        "downtime_reason",
        "target_output_qty",
        "actual_output_qty",
        "good_units",
        "rejected_units",
        "defect_type",
        "machine_temperature_c",
        "machine_vibration_mm_s",
        "estimated_loss_value",
    ]
    st.dataframe(filtered_df[display_cols].sort_values("date", ascending=False), use_container_width=True, hide_index=True)

st.caption("This demo uses deterministic analytics and risk scoring. Connect live PLC/MES/ERP/maintenance data before using it for operational decisions.")
