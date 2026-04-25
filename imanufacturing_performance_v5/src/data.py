from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "manufacturing_operations_data.csv"


@st.cache_data(show_spinner=False)
def load_operations_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load manufacturing operations data and normalize date columns."""
    path = Path(path)
    if not path.exists():
        return generate_sample_operations_data()

    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def generate_sample_operations_data(days: int = 90, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic sample dataset for local demos."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    plants = ["Plant A", "Plant B"]
    lines = ["Line 1", "Line 2", "Line 3"]
    machines = [f"M-{i:02d}" for i in range(1, 13)]
    shifts = ["Morning", "Evening", "Night"]
    products = ["Auto Bracket", "Pump Housing", "Gear Cover", "Valve Plate", "Bearing Cap"]
    downtime_reasons = [
        "Machine Breakdown",
        "Setup / Changeover",
        "Material Shortage",
        "Tooling Issue",
        "Quality Hold",
        "Minor Stops",
        "Planned Maintenance",
        "Utilities Issue",
    ]
    defect_types = ["None", "Dimension", "Surface", "Assembly", "Crack", "Packaging"]

    records: list[dict] = []
    for date in dates:
        for machine in machines:
            plant = plants[0] if int(machine.split("-")[1]) <= 6 else plants[1]
            line = lines[(int(machine.split("-")[1]) - 1) % len(lines)]
            for shift in shifts:
                planned_min = 480
                base_downtime = rng.gamma(shape=2.2, scale=12.0)
                if machine in {"M-04", "M-07", "M-11"}:
                    base_downtime *= 1.7
                if shift == "Night":
                    base_downtime *= 1.25
                downtime_min = min(float(base_downtime), 220.0)
                runtime_min = planned_min - downtime_min

                product = rng.choice(products)
                ideal_cycle_sec = rng.choice([38, 42, 48, 55, 62])
                target_output = int((planned_min * 60) / ideal_cycle_sec)
                performance_factor = rng.normal(0.88, 0.07)
                if line == "Line 2":
                    performance_factor -= 0.04
                actual_output = max(0, int(target_output * performance_factor * (runtime_min / planned_min)))

                defect_rate = max(0.002, rng.normal(0.035, 0.018))
                if shift == "Night":
                    defect_rate += 0.015
                if machine in {"M-07", "M-11"}:
                    defect_rate += 0.012
                rejected_units = min(actual_output, int(actual_output * defect_rate))
                good_units = actual_output - rejected_units

                reason_weights = np.array([0.22, 0.19, 0.13, 0.16, 0.09, 0.11, 0.06, 0.04])
                if machine in {"M-04", "M-07", "M-11"}:
                    reason_weights[0] += 0.14
                    reason_weights[3] += 0.06
                reason_weights = reason_weights / reason_weights.sum()
                downtime_reason = rng.choice(downtime_reasons, p=reason_weights)

                unit_margin = float(rng.choice([6.5, 8.0, 10.5, 12.0, 15.0]))
                estimated_loss = round((target_output - good_units) * unit_margin, 2)
                temperature = float(rng.normal(68, 6))
                vibration = float(rng.normal(2.4, 0.55))
                if machine in {"M-07", "M-11"}:
                    temperature += 7
                    vibration += 0.9

                records.append(
                    {
                        "date": date,
                        "plant_id": plant,
                        "line_id": line,
                        "machine_id": machine,
                        "shift": shift,
                        "product_id": product,
                        "planned_production_time_min": planned_min,
                        "runtime_min": round(runtime_min, 2),
                        "downtime_min": round(downtime_min, 2),
                        "downtime_reason": downtime_reason,
                        "ideal_cycle_time_sec": ideal_cycle_sec,
                        "target_output_qty": target_output,
                        "actual_output_qty": actual_output,
                        "good_units": good_units,
                        "rejected_units": rejected_units,
                        "defect_type": rng.choice(defect_types, p=[0.58, 0.15, 0.11, 0.07, 0.04, 0.05]),
                        "scrap_qty": int(rejected_units * rng.uniform(0.35, 0.75)),
                        "rework_qty": max(0, rejected_units - int(rejected_units * rng.uniform(0.35, 0.75))),
                        "maintenance_flag": bool(rng.random() < 0.08 or downtime_reason in {"Machine Breakdown", "Tooling Issue"}),
                        "machine_temperature_c": round(temperature, 2),
                        "machine_vibration_mm_s": round(vibration, 2),
                        "production_cost_per_unit": round(float(rng.normal(21, 4)), 2),
                        "selling_price_per_unit": round(float(rng.normal(34, 5)), 2),
                        "estimated_loss_value": estimated_loss,
                    }
                )

    return pd.DataFrame(records)


def apply_filters(
    df: pd.DataFrame,
    plants: list[str],
    lines: list[str],
    machines: list[str],
    shifts: list[str],
    products: list[str],
    date_range: tuple[pd.Timestamp, pd.Timestamp] | None,
) -> pd.DataFrame:
    """Apply dashboard filters to the operations dataframe."""
    filtered = df.copy()
    if date_range and "date" in filtered.columns:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]
    if plants:
        filtered = filtered[filtered["plant_id"].isin(plants)]
    if lines:
        filtered = filtered[filtered["line_id"].isin(lines)]
    if machines:
        filtered = filtered[filtered["machine_id"].isin(machines)]
    if shifts:
        filtered = filtered[filtered["shift"].isin(shifts)]
    if products:
        filtered = filtered[filtered["product_id"].isin(products)]
    return filtered
