
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "raw" / "macro_events.csv"
OUTPUT = ROOT / "data" / "processed" / "strategy_dataset.csv"

STRATEGIES = [
    {"name": "momentum", "lookback": 5, "threshold": 0.0},
    {"name": "momentum", "lookback": 10, "threshold": 0.2},
    {"name": "momentum", "lookback": 20, "threshold": 0.4},
    {"name": "mean_reversion", "lookback": 5, "threshold": 0.2},
    {"name": "mean_reversion", "lookback": 10, "threshold": 0.4},
    {"name": "mean_reversion", "lookback": 20, "threshold": 0.6},
]


def build_strategy_dataset(
    events: pd.DataFrame,
    days: int = 180,
) -> pd.DataFrame:
    """Create an explicitly synthetic strategy research dataset."""
    if days < 60:
        raise ValueError("Use at least 60 days for research data")

    required = {"timestamp_utc", "surprise", "event_name"}
    if not required.issubset(events.columns):
        raise ValueError(f"Input must contain {sorted(required)}")

    events = events.copy()
    events["timestamp_utc"] = pd.to_datetime(
        events["timestamp_utc"], utc=True, errors="raise"
    )
    events["surprise"] = pd.to_numeric(
        events["surprise"], errors="raise"
    )

    end = pd.Timestamp.now(tz="UTC").normalize()
    dates = pd.date_range(end=end, periods=days, freq="D")

    daily_macro = (
        events.assign(date=events["timestamp_utc"].dt.normalize())
        .groupby("date")
        .agg(
            daily_surprise=("surprise", "mean"),
            event_count=("event_name", "count"),
        )
    )

    base = pd.DataFrame({"date": dates})
    base = base.merge(
        daily_macro,
        left_on="date",
        right_index=True,
        how="left",
    )

    base["daily_surprise"] = base["daily_surprise"].fillna(0.0)
    base["event_count"] = base["event_count"].fillna(0).astype(int)

    # Only information available before the prediction date is used
    # for the macro signal.
    base["lagged_surprise"] = base["daily_surprise"].shift(1).fillna(0.0)

    rng = np.random.default_rng(2026)

    # Synthetic market returns: illustrative only, not actual market data.
    base["simulated_market_return"] = rng.normal(
        loc=0.0002, scale=0.01, size=len(base)
    )

    base["historical_volatility"] = (
        base["simulated_market_return"]
        .rolling(10, min_periods=3)
        .std()
        .fillna(0.0)
    )

    base["day_of_week"] = base["date"].dt.dayofweek
    base["month"] = base["date"].dt.month

    rows = []

    for strategy in STRATEGIES:
        frame = base.copy()

        frame["strategy"] = strategy["name"]
        frame["lookback"] = strategy["lookback"]
        frame["threshold"] = strategy["threshold"]

        momentum = (
            frame["simulated_market_return"]
            .rolling(strategy["lookback"], min_periods=1)
            .mean()
        )

        if strategy["name"] == "momentum":
            signal = np.sign(momentum)
        else:
            signal = -np.sign(momentum)

        signal = signal.where(
            momentum.abs() >= strategy["threshold"] / 100.0,
            0.0,
        )

        # Illustrative transaction cost, in return units.
        gross_return = signal * frame["simulated_market_return"].shift(-1)
        frame["target_return"] = gross_return - (
            (signal != 0).astype(float) * 0.0002
        )

        frame["target_win"] = (
            frame["target_return"] > 0
        ).astype("int64")

        frame["data_type"] = "synthetic_demo"
        rows.append(frame)

    result = pd.concat(rows, ignore_index=True)

    # The final date has no next-day target, so exclude it.
    result = result.dropna(subset=["target_return"]).copy()

    # Never export the future market return used to construct the target.
    result = result.drop(columns=["simulated_market_return"])

    return result.reset_index(drop=True)


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"{INPUT} not found. Generate macro event data first."
        )

    events = pd.read_csv(INPUT)
    dataset = build_strategy_dataset(events)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT, index=False)

    print(f"SUCCESS: Generated {len(dataset)} strategy observations")
    print(f"Strategies: {dataset['strategy'].nunique()}")
    print(f"Saved to: {OUTPUT}")
    print("\nObservations per strategy:")
    print(dataset.groupby("strategy").size().to_string())
    print("\nPreview:")
    print(dataset.head().to_string(index=False))


if __name__ == "__main__":
    main()
