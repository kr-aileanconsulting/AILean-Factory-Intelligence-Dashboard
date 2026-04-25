from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | str]:
    """Calculate core manufacturing KPIs."""
    if df.empty:
        return {
            "availability": 0.0,
            "performance": 0.0,
            "quality": 0.0,
            "oee": 0.0,
            "downtime_min": 0.0,
            "output_loss_qty": 0.0,
            "production_qty": 0.0,
            "good_units": 0.0,
            "rejected_units": 0.0,
            "defect_rate": 0.0,
            "estimated_loss_value": 0.0,
            "worst_machine": "N/A",
            "top_loss_reason": "N/A",
            "mttr": 0.0,
            "mtbf": 0.0,
        }

    planned = df["planned_production_time_min"].sum()
    runtime = df["runtime_min"].sum()
    downtime = df["downtime_min"].sum()
    target = df["target_output_qty"].sum()
    actual = df["actual_output_qty"].sum()
    good = df["good_units"].sum()
    rejected = df["rejected_units"].sum()

    availability = safe_divide(runtime, planned)
    performance = safe_divide(actual, target)
    quality = safe_divide(good, actual)
    oee = availability * performance * quality
    output_loss = max(target - good, 0)
    defect_rate = safe_divide(rejected, actual)

    machine_loss = df.groupby("machine_id", as_index=False)["downtime_min"].sum()
    worst_machine = machine_loss.sort_values("downtime_min", ascending=False).iloc[0]["machine_id"]

    reason_loss = df.groupby("downtime_reason", as_index=False)["downtime_min"].sum()
    top_loss_reason = reason_loss.sort_values("downtime_min", ascending=False).iloc[0]["downtime_reason"]

    failure_events = df[df["downtime_reason"].isin(["Machine Breakdown", "Tooling Issue", "Utilities Issue"])]
    mttr = safe_divide(failure_events["downtime_min"].sum(), len(failure_events))
    mtbf = safe_divide(runtime, len(failure_events))

    return {
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "oee": oee,
        "downtime_min": float(downtime),
        "output_loss_qty": float(output_loss),
        "production_qty": float(actual),
        "good_units": float(good),
        "rejected_units": float(rejected),
        "defect_rate": defect_rate,
        "estimated_loss_value": float(df["estimated_loss_value"].sum()),
        "worst_machine": str(worst_machine),
        "top_loss_reason": str(top_loss_reason),
        "mttr": float(mttr),
        "mtbf": float(mtbf),
    }


def add_oee_columns(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["availability"] = enriched.apply(
        lambda r: safe_divide(r["runtime_min"], r["planned_production_time_min"]), axis=1
    )
    enriched["performance"] = enriched.apply(
        lambda r: safe_divide(r["actual_output_qty"], r["target_output_qty"]), axis=1
    )
    enriched["quality"] = enriched.apply(
        lambda r: safe_divide(r["good_units"], r["actual_output_qty"]), axis=1
    )
    enriched["oee"] = enriched["availability"] * enriched["performance"] * enriched["quality"]
    enriched["defect_rate"] = enriched.apply(
        lambda r: safe_divide(r["rejected_units"], r["actual_output_qty"]), axis=1
    )
    enriched["maintenance_risk_score"] = np.clip(
        (enriched["downtime_min"] / enriched["planned_production_time_min"]) * 40
        + (enriched["machine_temperature_c"] - 60).clip(lower=0) * 1.4
        + (enriched["machine_vibration_mm_s"] - 2).clip(lower=0) * 18
        + enriched["defect_rate"] * 100,
        0,
        100,
    )
    return enriched


def aggregate_oee(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grouped = df.groupby(group_col, as_index=False).agg(
        planned=("planned_production_time_min", "sum"),
        runtime=("runtime_min", "sum"),
        target=("target_output_qty", "sum"),
        actual=("actual_output_qty", "sum"),
        good=("good_units", "sum"),
        downtime=("downtime_min", "sum"),
        rejected=("rejected_units", "sum"),
        loss_value=("estimated_loss_value", "sum"),
        risk=("maintenance_risk_score", "mean"),
    )
    grouped["availability"] = grouped.apply(lambda r: safe_divide(r["runtime"], r["planned"]), axis=1)
    grouped["performance"] = grouped.apply(lambda r: safe_divide(r["actual"], r["target"]), axis=1)
    grouped["quality"] = grouped.apply(lambda r: safe_divide(r["good"], r["actual"]), axis=1)
    grouped["oee"] = grouped["availability"] * grouped["performance"] * grouped["quality"]
    grouped["defect_rate"] = grouped.apply(lambda r: safe_divide(r["rejected"], r["actual"]), axis=1)
    return grouped
