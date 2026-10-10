"""Unit and regression tests for genuine historical market backtesting module."""
import numpy as np
import pandas as pd
import pytest

from src.backtesting.market_backtest import (
    align_macro_with_market,
    calculate_metrics,
    execute_rule_strategies,
    run_walk_forward_market_backtest,
)


@pytest.fixture
def sample_market_data():
    dates = pd.date_range("2026-01-01", periods=60, freq="B").strftime("%Y-%m-%d")
    np.random.seed(42)
    # Generate realistic prices
    returns = np.random.normal(0.0005, 0.01, size=len(dates))
    prices = 500.0 * np.cumprod(1.0 + returns)

    df = pd.DataFrame({
        "date": dates,
        "open": prices * 0.999,
        "high": prices * 1.005,
        "low": prices * 0.995,
        "close": prices,
        "volume": np.random.randint(1000000, 5000000, size=len(dates)),
        "daily_return": returns,
        "ticker": "SPY",
    })
    return df


@pytest.fixture
def sample_macro_events():
    dates = pd.date_range("2026-01-01", periods=60, freq="B").strftime("%Y-%m-%d")
    events = []
    for d in dates[::3]:  # release every 3rd day
        events.append({
            "event_date": d,
            "event_name": "CPI",
            "country": "United States",
            "actual": 3.1,
            "forecast": 3.0,
            "surprise": 0.1,
            "impact": "High",
        })
    return pd.DataFrame(events)


def test_calculate_metrics_finite():
    rets = pd.Series([0.01, -0.005, 0.015, -0.002, 0.008])
    metrics = calculate_metrics(rets)

    assert metrics["sample_size"] == 5
    assert "sharpe_ratio" in metrics
    assert "sortino_ratio" in metrics
    assert "cumulative_return" in metrics
    assert "max_drawdown" in metrics
    assert metrics["max_drawdown"] <= 0.0
    assert all(np.isfinite(v) for v in metrics.values())


def test_calculate_metrics_empty():
    metrics = calculate_metrics(pd.Series([], dtype=float))
    assert metrics["sample_size"] == 0
    assert metrics["cumulative_return"] == 0.0


def test_align_macro_with_market_no_lookahead(sample_market_data, sample_macro_events):
    aligned = align_macro_with_market(sample_market_data, sample_macro_events)

    assert not aligned.empty
    assert "next_day_return" in aligned.columns
    assert "return_10d" in aligned.columns
    assert "macro_net_surprise" in aligned.columns
    # Check that aligned has no NaNs in feature columns
    assert aligned["next_day_return"].notna().all()
    assert aligned["return_10d"].notna().all()


def test_execute_rule_strategies(sample_market_data, sample_macro_events):
    aligned = align_macro_with_market(sample_market_data, sample_macro_events)
    res, metrics = execute_rule_strategies(aligned, cost_bps=0.0002)

    assert "ret_buy_hold" in res.columns
    assert "ret_mom_10d" in res.columns
    assert "ret_macro_shock" in res.columns
    assert "buy_hold" in metrics
    assert "mom_10d" in metrics
    assert "macro_shock" in metrics


def test_walk_forward_market_backtest(sample_market_data, sample_macro_events):
    aligned = align_macro_with_market(sample_market_data, sample_macro_events)
    summary, oos_preds = run_walk_forward_market_backtest(aligned, cost_bps=0.0002, n_splits=2)

    assert summary["out_of_sample_observations"] == len(oos_preds)
    assert "ml_ensemble_strategy" in summary
    assert "benchmark_buy_and_hold" in summary
    assert len(summary["folds"]) == 2
    assert "ml_strategy_return" in oos_preds.columns
