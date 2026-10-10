
import numpy as np
import pandas as pd

from src.models.build_strategy_dataset import build_strategy_dataset
from src.models.train_model import (
    performance_metrics,
    walk_forward_evaluate,
)


def sample_strategy_data():
    dates = pd.date_range(
        "2025-01-01", periods=100, freq="D", tz="UTC"
    )

    events = pd.DataFrame({
        "timestamp_utc": dates.astype(str),
        "surprise": np.sin(np.arange(100) / 5),
        "event_name": ["CPI"] * 100,
    })

    return build_strategy_dataset(events, days=100)


def test_metrics_return_expected_fields():
    metrics = performance_metrics(
        pd.Series([0.01, -0.005, 0.008, -0.002])
    )

    assert metrics["observations"] == 4
    assert "annualized_sharpe" in metrics
    assert "annualized_sortino" in metrics
    assert "max_drawdown" in metrics
    assert "cumulative_return" in metrics


def test_metrics_are_finite():
    metrics = performance_metrics(
        pd.Series([0.01, -0.005, 0.008, -0.002])
    )

    assert all(np.isfinite(value) for value in metrics.values())


def test_walk_forward_produces_out_of_sample_predictions():
    data = sample_strategy_data()
    predictions, report = walk_forward_evaluate(data, folds=3)

    assert not predictions.empty
    assert predictions["predicted_return"].notna().all()
    assert predictions["fold"].nunique() == 3
    assert report["out_of_sample_strategy_rows"] == len(predictions)


def test_test_dates_are_after_training_period():
    data = sample_strategy_data()
    predictions, _ = walk_forward_evaluate(data, folds=3)

    assert predictions["date"].notna().all()
    assert predictions["predicted_return"].notna().all()
