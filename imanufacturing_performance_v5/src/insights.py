from __future__ import annotations

import pandas as pd

from src.kpis import aggregate_oee


def build_action_recommendations(df: pd.DataFrame, kpis: dict) -> list[dict[str, str]]:
    """Generate deterministic recommendations from the filtered data."""
    if df.empty:
        return [{"title": "No data available", "body": "Adjust the filters to bring records back into the dashboard."}]

    machine = aggregate_oee(df, "machine_id").sort_values("downtime", ascending=False).iloc[0]
    shift = aggregate_oee(df, "shift").sort_values("defect_rate", ascending=False).iloc[0]
    line = aggregate_oee(df, "line_id").sort_values("oee", ascending=True).iloc[0]
    reason = df.groupby("downtime_reason", as_index=False)["downtime_min"].sum().sort_values("downtime_min", ascending=False).iloc[0]
    risk = aggregate_oee(df, "machine_id").sort_values("risk", ascending=False).iloc[0]

    actions = [
        {
            "title": f"Attack the largest downtime pocket: {machine['machine_id']}",
            "body": f"{machine['machine_id']} contributed {machine['downtime']:.0f} downtime minutes. Start with the recurring cause '{reason['downtime_reason']}' and check maintenance history before the next high-volume run.",
        },
        {
            "title": f"Stabilize quality on {shift['shift']} shift",
            "body": f"The {shift['shift']} shift has the highest defect rate at {shift['defect_rate'] * 100:.1f}%. Run a first-hour quality gate and verify tooling setup before production ramps up.",
        },
        {
            "title": f"Recover OEE on {line['line_id']}",
            "body": f"{line['line_id']} is the lowest-performing line with OEE at {line['oee'] * 100:.1f}%. Separate losses into availability, speed loss, and quality loss before assigning corrective action.",
        },
        {
            "title": f"Prioritize inspection for {risk['machine_id']}",
            "body": f"{risk['machine_id']} has the highest maintenance risk score at {risk['risk']:.0f}/100. The risk score uses downtime, temperature, vibration, and defect pattern signals.",
        },
    ]
    return actions


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"
