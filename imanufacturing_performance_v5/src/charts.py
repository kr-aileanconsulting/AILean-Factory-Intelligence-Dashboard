from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.kpis import aggregate_oee
from src.styles import COLORS, plot_layout


def oee_trend(df: pd.DataFrame) -> go.Figure:
    daily = aggregate_oee(df, "date").sort_values("date")
    daily["oee_pct"] = daily["oee"] * 100
    fig = px.line(daily, x="date", y="oee_pct", markers=True, title="OEE Trend")
    fig.add_hline(y=75, line_dash="dash", annotation_text="Target 75%")
    fig.update_traces(line_width=3, marker_size=6)
    fig.update_layout(**plot_layout())
    fig.update_yaxes(title="OEE %", ticksuffix="%")
    return fig


def oee_by_machine(df: pd.DataFrame) -> go.Figure:
    agg = aggregate_oee(df, "machine_id").sort_values("oee", ascending=True)
    agg["oee_pct"] = agg["oee"] * 100
    fig = px.bar(agg, x="oee_pct", y="machine_id", orientation="h", color="oee_pct", color_continuous_scale="RdYlGn", title="OEE by Machine")
    fig.update_layout(**plot_layout())
    fig.update_xaxes(title="OEE %", ticksuffix="%")
    fig.update_yaxes(title="Machine")
    return fig


def downtime_pareto(df: pd.DataFrame) -> go.Figure:
    pareto = df.groupby("downtime_reason", as_index=False)["downtime_min"].sum().sort_values("downtime_min", ascending=False)
    pareto["cum_pct"] = pareto["downtime_min"].cumsum() / pareto["downtime_min"].sum() * 100
    fig = go.Figure()
    fig.add_bar(x=pareto["downtime_reason"], y=pareto["downtime_min"], name="Downtime minutes", marker_color=COLORS[0])
    fig.add_scatter(x=pareto["downtime_reason"], y=pareto["cum_pct"], name="Cumulative %", yaxis="y2", mode="lines+markers", line={"width": 3})
    fig.update_layout(
        **plot_layout("Downtime Pareto"),
        yaxis={"title": "Minutes"},
        yaxis2={"title": "Cumulative %", "overlaying": "y", "side": "right", "ticksuffix": "%", "range": [0, 105]},
        xaxis={"tickangle": -25},
    )
    return fig


def loss_by_shift(df: pd.DataFrame) -> go.Figure:
    agg = aggregate_oee(df, "shift")
    agg["loss_value_k"] = agg["loss_value"] / 1000
    fig = px.bar(agg, x="shift", y="loss_value_k", color="shift", color_discrete_sequence=COLORS, title="Estimated Loss by Shift")
    fig.update_layout(**plot_layout())
    fig.update_yaxes(title="Estimated loss ($K)", tickprefix="$")
    return fig


def quality_heatmap(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["machine_id", "shift"], as_index=False).agg(rejected=("rejected_units", "sum"), actual=("actual_output_qty", "sum"))
    agg["defect_rate"] = agg.apply(lambda r: r["rejected"] / r["actual"] * 100 if r["actual"] else 0, axis=1)
    pivot = agg.pivot(index="machine_id", columns="shift", values="defect_rate").fillna(0)
    fig = px.imshow(pivot, text_auto=".1f", aspect="auto", color_continuous_scale="OrRd", title="Defect Rate Heatmap")
    fig.update_layout(**plot_layout())
    fig.update_coloraxes(colorbar_title="Defect %")
    return fig


def risk_by_machine(df: pd.DataFrame) -> go.Figure:
    agg = aggregate_oee(df, "machine_id").sort_values("risk", ascending=False).head(8)
    fig = px.bar(agg, x="machine_id", y="risk", color="risk", color_continuous_scale="Turbo", title="Maintenance Risk Score")
    fig.update_layout(**plot_layout())
    fig.update_yaxes(title="Risk score", range=[0, 100])
    return fig


def oee_loss_tree(df: pd.DataFrame) -> go.Figure:
    agg = aggregate_oee(df, "line_id")
    availability_loss = (1 - agg["availability"]).clip(lower=0).sum()
    performance_loss = (1 - agg["performance"]).clip(lower=0).sum()
    quality_loss = (1 - agg["quality"]).clip(lower=0).sum()
    labels = ["Total Loss", "Availability Loss", "Performance Loss", "Quality Loss", "Downtime", "Slow Cycle", "Defects/Rework"]
    parents = ["", "Total Loss", "Total Loss", "Total Loss", "Availability Loss", "Performance Loss", "Quality Loss"]
    values = [availability_loss + performance_loss + quality_loss, availability_loss, performance_loss, quality_loss, availability_loss, performance_loss, quality_loss]
    fig = px.treemap(names=labels, parents=parents, values=values, title="OEE Loss Tree")
    fig.update_layout(**plot_layout())
    return fig


def production_by_line(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("line_id", as_index=False).agg(good=("good_units", "sum"), rejected=("rejected_units", "sum"))
    fig = px.bar(agg, x="line_id", y=["good", "rejected"], barmode="stack", title="Good vs Rejected Output by Line", color_discrete_sequence=[COLORS[3], COLORS[2]])
    fig.update_layout(**plot_layout())
    fig.update_yaxes(title="Units")
    return fig
