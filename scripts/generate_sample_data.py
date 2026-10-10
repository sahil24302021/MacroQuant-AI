
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "macro_events.csv"


def generate_macro_events(days: int = 180) -> pd.DataFrame:
    """Generate reproducible synthetic macroeconomic events."""
    if days < 1:
        raise ValueError("days must be at least 1")

    rng = np.random.default_rng(42)

    dates = pd.date_range(
        end=pd.Timestamp.now(tz="UTC").normalize(),
        periods=days,
        freq="D",
    )

    event_types = [
        ("CPI", "Inflation"),
        ("FOMC", "Monetary Policy"),
        ("NFP", "Employment"),
        ("GDP", "Growth"),
        ("PMI", "Business Activity"),
    ]

    rows = []

    for date in dates:
        if rng.random() > 0.23:
            continue

        event, category = event_types[
            rng.integers(0, len(event_types))
        ]

        forecast = round(float(rng.normal(3.0, 0.8)), 3)
        actual = round(
            float(forecast + rng.normal(0, 0.35)), 3
        )

        rows.append(
            {
                "event_id": f"SYN-{len(rows) + 1:05d}",
                "timestamp_utc": date.isoformat(),
                "event_name": event,
                "category": category,
                "forecast": forecast,
                "actual": actual,
                "surprise": round(actual - forecast, 3),
                "source": "synthetic_demo",
            }
        )

    columns = [
        "event_id",
        "timestamp_utc",
        "event_name",
        "category",
        "forecast",
        "actual",
        "surprise",
        "source",
    ]

    return pd.DataFrame(rows, columns=columns)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate_macro_events()

    assert not df.empty
    assert df["event_id"].is_unique
    assert df["timestamp_utc"].notna().all()

    expected = df["actual"] - df["forecast"]
    assert np.allclose(
        df["surprise"], expected, atol=1e-12
    )

    df.to_csv(OUTPUT, index=False)

    print(f"SUCCESS: Generated {len(df)} synthetic events")
    print(f"Saved to: {OUTPUT}")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()
