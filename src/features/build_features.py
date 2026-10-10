
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "raw" / "macro_events.csv"
OUTPUT = ROOT / "data" / "processed" / "macro_features.csv"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Validate macro events and construct research features."""

    required = {
        "event_id",
        "timestamp_utc",
        "event_name",
        "category",
        "forecast",
        "actual",
        "surprise",
        "source",
    }

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = df.copy()

    if result.empty:
        raise ValueError("Input dataset is empty")

    if result["event_id"].isna().any():
        raise ValueError("event_id contains missing values")

    if result["event_id"].duplicated().any():
        raise ValueError("event_id must be unique")

    for column in ["forecast", "actual", "surprise"]:
        result[column] = pd.to_numeric(
            result[column], errors="raise"
        )

        if not np.isfinite(result[column]).all():
            raise ValueError(f"{column} contains invalid values")

    timestamps = pd.to_datetime(
        result["timestamp_utc"], utc=True, errors="raise"
    )

    result["timestamp_utc"] = timestamps
    result = result.sort_values(
        ["timestamp_utc", "event_id"]
    ).reset_index(drop=True)

    expected_surprise = result["actual"] - result["forecast"]

    if not np.allclose(
        result["surprise"],
        expected_surprise,
        atol=1e-9,
    ):
        raise ValueError("surprise does not match actual - forecast")

    # Time-based features
    result["year"] = timestamps.dt.year
    result["month"] = timestamps.dt.month
    result["day_of_week"] = timestamps.dt.dayofweek

    hour = timestamps.dt.hour + timestamps.dt.minute / 60.0
    result["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    result["hour_cos"] = np.cos(2 * np.pi * hour / 24)

    # Leakage-safe historical statistics: an event only uses past observations
    exp_mean = (
        result.groupby("event_name")["surprise"]
        .expanding()
        .mean()
        .shift(1)
        .reset_index(level=0, drop=True)
    )
    exp_std = (
        result.groupby("event_name")["surprise"]
        .expanding()
        .std()
        .shift(1)
        .reset_index(level=0, drop=True)
        .fillna(0.0)
    )

    result["surprise_zscore"] = (
        (result["surprise"] - exp_mean)
        / exp_std.replace(0.0, np.nan)
    ).fillna(0.0)

    # Descriptive sentiment proxy, not a trading signal.
    result["surprise_direction"] = np.sign(result["surprise"])

    return result


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input not found: {INPUT}. Run the sample data generator first."
        )

    raw = pd.read_csv(INPUT)
    features = build_features(raw)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(OUTPUT, index=False)

    print(f"SUCCESS: Built {len(features)} feature rows")
    print(f"Saved to: {OUTPUT}")
    print("\nAvailable columns:")
    print(", ".join(features.columns))


if __name__ == "__main__":
    main()
