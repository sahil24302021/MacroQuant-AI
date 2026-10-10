
import pandas as pd
import pytest

from src.models.build_strategy_dataset import build_strategy_dataset


def sample_events():
    dates = pd.date_range(
        "2026-01-01", periods=80, freq="D", tz="UTC"
    )
    return pd.DataFrame({
        "timestamp_utc": dates.astype(str),
        "surprise": [0.2, -0.1, 0.3, -0.2] * 20,
        "event_name": ["CPI", "NFP", "GDP", "PMI"] * 20,
    })


def test_dataset_has_six_strategy_permutations():
    result = build_strategy_dataset(sample_events(), days=80)
    assert result["strategy"].nunique() == 2
    assert result.groupby(
        ["strategy", "lookback", "threshold"]
    ).ngroups == 6


def test_targets_are_valid():
    result = build_strategy_dataset(sample_events(), days=80)
    assert result["target_return"].notna().all()
    assert result["target_win"].isin([0, 1]).all()


def test_future_market_return_is_not_exported():
    result = build_strategy_dataset(sample_events(), days=80)
    assert "simulated_market_return" not in result.columns


def test_short_period_is_rejected():
    with pytest.raises(ValueError):
        build_strategy_dataset(sample_events(), days=30)
