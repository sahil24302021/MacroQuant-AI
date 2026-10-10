"""Genuine Historical Market Backtest Module.

Downloads real historical price data for liquid market benchmarks (default: SPY via Yahoo Finance),
aligns macroeconomic event surprises and news sentiment signals without lookahead bias,
and conducts chronological expanding walk-forward evaluations with realistic transaction costs (2 bps).
"""
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]


def download_market_prices(
    ticker: str = "SPY",
    start_date: str = "2025-10-01",
    end_date: str = "2026-10-11",
    output_path: Path | None = None,
) -> pd.DataFrame:
    """Download daily OHLCV from Yahoo Finance via yfinance, compute returns, and save locally."""
    import yfinance as yf

    dest = output_path or ROOT / "data" / "processed" / "market_prices.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading historical prices for %s (%s to %s)...", ticker, start_date, end_date)
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

    if df.empty:
        raise RuntimeError(f"No market price data returned for {ticker} from Yahoo Finance.")

    # Normalize dataframe index and column names
    df = df.reset_index()
    # Format date as YYYY-MM-DD
    if "Date" in df.columns:
        df["date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    elif "date" not in df.columns:
        df["date"] = pd.to_datetime(df.index).dt.tz_localize(None).dt.strftime("%Y-%m-%d")

    # Rename to lowercase
    col_map = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    df = df.rename(columns=col_map)
    cols = ["date", "open", "high", "low", "close", "volume"]
    df = df[[c for c in cols if c in df.columns]].copy()

    # Calculate daily close-to-close returns
    df["daily_return"] = df["close"].pct_change()
    df["ticker"] = ticker
    df["data_provenance"] = "real_yahoo_finance"

    df = df.dropna(subset=["daily_return"]).reset_index(drop=True)
    df.to_csv(dest, index=False)
    logger.info("Saved %d price rows for %s to %s", len(df), ticker, dest)
    return df


def align_macro_with_market(
    market_df: pd.DataFrame,
    macro_events_df: pd.DataFrame,
    news_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Align macroeconomic events and sentiment features with market prices without lookahead bias.

    Features computed on date t predict returns on date t+1.
    """
    mkt = market_df.copy()
    mkt["date"] = pd.to_datetime(mkt["date"]).dt.strftime("%Y-%m-%d")
    mkt = mkt.sort_values("date").reset_index(drop=True)

    # Compute price-based features on date t
    mkt["return_1d"] = mkt["daily_return"]
    mkt["return_5d"] = mkt["close"].pct_change(5)
    mkt["return_10d"] = mkt["close"].pct_change(10)
    mkt["volatility_10d"] = mkt["daily_return"].rolling(10).std()
    mkt["next_day_return"] = mkt["daily_return"].shift(-1)

    # Aggregate macro events on date t
    macro_daily: dict[str, dict[str, Any]] = {}
    if macro_events_df is not None and not macro_events_df.empty:
        evs = macro_events_df.copy()
        if "event_date" in evs.columns:
            evs["event_date"] = pd.to_datetime(evs["event_date"]).dt.strftime("%Y-%m-%d")
            grouped = evs.groupby("event_date")
            for dt_str, grp in grouped:
                surprises = grp["surprise"].dropna().values if "surprise" in grp.columns else []
                net_surp = float(np.sum(surprises)) if len(surprises) > 0 else 0.0
                macro_daily[dt_str] = {
                    "macro_event_count": len(grp),
                    "macro_net_surprise": net_surp,
                    "macro_high_impact_count": int((grp["impact"].str.lower() == "high").sum()) if "impact" in grp.columns else 0,
                }

    # Aggregate news sentiment on date t
    news_daily: dict[str, float] = {}
    if news_df is not None and not news_df.empty and "published_at" in news_df.columns:
        valid_news = news_df.dropna(subset=["published_at"]).copy()
        valid_news["pub_date"] = pd.to_datetime(valid_news["published_at"], errors="coerce").dt.strftime("%Y-%m-%d")
        for dt_str, grp in valid_news.groupby("pub_date"):
            if dt_str:
                news_daily[dt_str] = float(grp["sentiment_score"].mean()) if "sentiment_score" in grp.columns else 0.0

    # Merge into market dataframe
    mkt["macro_event_count"] = mkt["date"].map(lambda d: macro_daily.get(d, {}).get("macro_event_count", 0))
    mkt["macro_net_surprise"] = mkt["date"].map(lambda d: macro_daily.get(d, {}).get("macro_net_surprise", 0.0))
    mkt["macro_high_impact_count"] = mkt["date"].map(lambda d: macro_daily.get(d, {}).get("macro_high_impact_count", 0))
    mkt["macro_sentiment"] = mkt["date"].map(lambda d: news_daily.get(d, 0.0))

    # Rolling macro features
    mkt["macro_surprise_5d"] = mkt["macro_net_surprise"].rolling(5, min_periods=1).sum()

    # Drop rows without complete feature history or without next_day_return
    mkt = mkt.dropna(subset=["return_10d", "volatility_10d", "next_day_return"]).reset_index(drop=True)
    return mkt


def calculate_metrics(returns: pd.Series, risk_free_rate: float = 0.0) -> dict[str, float]:
    """Calculate institutional performance metrics for a return series."""
    clean_rets = returns.dropna()
    if len(clean_rets) == 0:
        return {
            "cumulative_return": 0.0,
            "annualized_return": 0.0,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "sample_size": 0,
        }

    cum_ret = float(np.prod(1.0 + clean_rets) - 1.0)
    mean_ret = float(clean_rets.mean())
    std_ret = float(clean_rets.std())
    ann_factor = np.sqrt(252)

    ann_ret = float(mean_ret * 252)
    ann_vol = float(std_ret * ann_factor) if std_ret > 0 else 0.0
    sharpe = float((mean_ret - risk_free_rate) / std_ret * ann_factor) if std_ret > 0 else 0.0

    downside = clean_rets[clean_rets < 0]
    downside_std = float(downside.std()) if len(downside) > 1 else std_ret
    sortino = float(mean_ret / downside_std * ann_factor) if downside_std > 0 else 0.0

    # Max drawdown
    wealth = (1.0 + clean_rets).cumprod()
    peak = wealth.cummax()
    drawdown = (wealth - peak) / peak
    max_dd = float(drawdown.min()) if not drawdown.empty else 0.0
    win_rate = float((clean_rets > 0).mean())

    return {
        "cumulative_return": round(cum_ret, 6),
        "annualized_return": round(ann_ret, 6),
        "annualized_volatility": round(ann_vol, 6),
        "sharpe_ratio": round(sharpe, 4),
        "sortino_ratio": round(sortino, 4),
        "max_drawdown": round(max_dd, 6),
        "win_rate": round(win_rate, 4),
        "sample_size": len(clean_rets),
    }


def execute_rule_strategies(
    df: pd.DataFrame,
    cost_bps: float = 0.0002,
) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    """Execute rule-based quantitative strategies on real SPY price data with transaction costs."""
    res = df.copy()

    # 1. Benchmark: Buy & Hold SPY
    res["sig_buy_hold"] = 1.0

    # 2. Price Momentum (10-day lookback)
    res["sig_mom_10d"] = np.where(res["return_10d"] > 0, 1.0, -1.0)

    # 3. Price Momentum (5-day lookback)
    res["sig_mom_5d"] = np.where(res["return_5d"] > 0, 1.0, -1.0)

    # 4. Mean Reversion (5-day vs 10-day volatility)
    threshold = 1.2 * res["volatility_10d"]
    sig_mr = np.zeros(len(res))
    sig_mr[res["return_5d"] > threshold] = -1.0
    sig_mr[res["return_5d"] < -threshold] = 1.0
    res["sig_mean_rev_5d"] = sig_mr

    # 5. Macro Surprise Strategy (Trade on macro news shock)
    sig_macro = np.zeros(len(res))
    sig_macro[res["macro_surprise_5d"] > 0] = 1.0
    sig_macro[res["macro_surprise_5d"] < 0] = -1.0
    res["sig_macro_shock"] = sig_macro

    # Compute returns after transaction costs
    strategies = ["buy_hold", "mom_10d", "mom_5d", "mean_rev_5d", "macro_shock"]
    metrics_summary = {}

    for strat in strategies:
        sig_col = f"sig_{strat}"
        pos_change = res[sig_col].diff().abs().fillna(0.0)
        costs = pos_change * cost_bps
        ret_col = f"ret_{strat}"
        res[ret_col] = res[sig_col] * res["next_day_return"] - costs
        metrics_summary[strat] = calculate_metrics(res[ret_col])

    return res, metrics_summary


def run_walk_forward_market_backtest(
    df: pd.DataFrame,
    cost_bps: float = 0.0002,
    n_splits: int = 3,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Run chronological expanding walk-forward evaluation on genuine market data.

    Trains Random Forest on past folds, predicts out-of-sample strategy weights,
    and applies transaction costs strictly on unseen future data.
    """
    feature_cols = [
        "return_1d",
        "return_5d",
        "return_10d",
        "volatility_10d",
        "macro_event_count",
        "macro_net_surprise",
        "macro_surprise_5d",
        "macro_sentiment",
    ]

    n_samples = len(df)
    min_train = int(n_samples * 0.5)
    test_chunk = (n_samples - min_train) // n_splits

    predictions_records = []
    fold_metrics = []

    for fold in range(n_splits):
        train_end = min_train + fold * test_chunk
        test_end = n_samples if fold == n_splits - 1 else train_end + test_chunk

        train_data = df.iloc[:train_end].copy()
        test_data = df.iloc[train_end:test_end].copy()

        # Fit scaler on training data ONLY
        scaler = StandardScaler()
        X_train = scaler.fit_transform(train_data[feature_cols])
        y_train = train_data["next_day_return"].values

        # Model: Random Forest Regressor
        model = RandomForestRegressor(n_estimators=100, max_depth=4, random_state=42 + fold)
        model.fit(X_train, y_train)

        # Predict strictly on unseen out-of-sample test data
        X_test = scaler.transform(test_data[feature_cols])
        pred_returns = model.predict(X_test)

        # Dynamic strategy allocation rule:
        # Long if predicted return is positive, cash/short if negative
        positions = np.where(pred_returns > 0, 1.0, -1.0)
        test_data["pred_return"] = pred_returns
        test_data["ml_position"] = positions
        test_data["fold"] = fold + 1

        # Transaction costs on position changes
        pos_diff = np.abs(np.diff(positions, prepend=positions[0]))
        frictions = pos_diff * cost_bps
        test_data["ml_strategy_return"] = positions * test_data["next_day_return"].values - frictions
        test_data["benchmark_return"] = test_data["next_day_return"].values  # Buy & Hold SPY

        fold_perf = calculate_metrics(test_data["ml_strategy_return"])
        fold_perf["fold"] = fold + 1
        fold_perf["test_start"] = test_data["date"].iloc[0]
        fold_perf["test_end"] = test_data["date"].iloc[-1]
        fold_metrics.append(fold_perf)

        predictions_records.append(test_data)

    all_oos = pd.concat(predictions_records, ignore_index=True)
    overall_ml_metrics = calculate_metrics(all_oos["ml_strategy_return"])
    overall_bm_metrics = calculate_metrics(all_oos["benchmark_return"])

    summary = {
        "ticker": df["ticker"].iloc[0] if "ticker" in df.columns else "SPY",
        "data_provenance": "real_yahoo_finance",
        "evaluation_type": "chronological_walk_forward_out_of_sample",
        "total_observations": n_samples,
        "out_of_sample_observations": len(all_oos),
        "out_of_sample_date_range": {
            "start": all_oos["date"].iloc[0],
            "end": all_oos["date"].iloc[-1],
        },
        "transaction_cost_bps": cost_bps * 10000,
        "ml_ensemble_strategy": overall_ml_metrics,
        "benchmark_buy_and_hold": overall_bm_metrics,
        "folds": fold_metrics,
    }

    return summary, all_oos
