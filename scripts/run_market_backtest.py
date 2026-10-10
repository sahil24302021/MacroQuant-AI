"""Driver script for genuine historical market backtest on real SPY data.

Downloads authentic daily price series for SPY (SPDR S&P 500 ETF Trust) via Yahoo Finance,
merges real macroeconomic events and news sentiment signals without lookahead bias,
and conducts chronological expanding walk-forward out-of-sample backtests with 2 bps transaction costs.
"""
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.backtesting.market_backtest import (
    align_macro_with_market,
    download_market_prices,
    execute_rule_strategies,
    run_walk_forward_market_backtest,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("market_backtest")


def main():
    logger.info("Starting genuine historical market backtest pipeline...")

    # 1. Download real daily market prices for SPY (SPDR S&P 500 ETF Trust)
    market_df = download_market_prices(
        ticker="SPY",
        start_date="2025-10-01",
        end_date="2026-10-11",
    )
    logger.info("Retrieved %d daily price bars for SPY.", len(market_df))

    # 2. Load real macroeconomic events and news datasets
    macro_path = ROOT / "data" / "processed" / "real_macro_events.csv"
    news_path = ROOT / "data" / "processed" / "real_macro_news.csv"

    macro_df = pd.read_csv(macro_path) if macro_path.exists() else pd.DataFrame()
    news_df = pd.read_csv(news_path) if news_path.exists() else pd.DataFrame()
    logger.info("Loaded %d real macro events and %d real news items.", len(macro_df), len(news_df))

    # 3. Align features with market returns strictly without lookahead bias
    aligned_df = align_macro_with_market(market_df, macro_df, news_df)
    logger.info("Aligned market-macro feature dataset: %d trading observations.", len(aligned_df))

    # 4. Execute rule-based quantitative strategies
    _, rule_metrics = execute_rule_strategies(aligned_df, cost_bps=0.0002)

    # 5. Run chronological expanding walk-forward ML evaluation
    ml_summary, oos_predictions = run_walk_forward_market_backtest(
        aligned_df,
        cost_bps=0.0002,
        n_splits=3,
    )

    # Merge rule metrics into summary
    ml_summary["rule_based_strategies"] = rule_metrics

    # Save outputs
    eval_json_path = ROOT / "reports" / "market_backtest_evaluation.json"
    eval_json_path.parent.mkdir(parents=True, exist_ok=True)
    eval_json_path.write_text(json.dumps(ml_summary, indent=2), encoding="utf-8")
    logger.info("Saved backtest metrics to %s", eval_json_path.relative_to(ROOT))

    preds_path = ROOT / "reports" / "market_backtest_predictions.csv"
    oos_predictions.to_csv(preds_path, index=False)
    logger.info("Saved out-of-sample prediction logs to %s", preds_path.relative_to(ROOT))

    print("\n" + "=" * 60)
    print("GENUINE HISTORICAL MARKET BACKTEST RESULTS (SPY, REAL DATA)")
    print("=" * 60)
    print(f"Instrument:                  {ml_summary['ticker']} (S&P 500 ETF Trust)")
    print(f"Data Provenance:             {ml_summary['data_provenance']}")
    print(f"Total Observations:          {ml_summary['total_observations']} days")
    print(f"Out-of-Sample Period:        {ml_summary['out_of_sample_date_range']['start']} to {ml_summary['out_of_sample_date_range']['end']}")
    print(f"Out-of-Sample Observations:  {ml_summary['out_of_sample_observations']} days (3 Expanding Folds)")
    print(f"Modeled Transaction Costs:   {ml_summary['transaction_cost_bps']:.1f} bps per trade")
    print("-" * 60)

    ml_perf = ml_summary["ml_ensemble_strategy"]
    bm_perf = ml_summary["benchmark_buy_and_hold"]
    print(f"ML Dynamic Strategy Sharpe:  {ml_perf['sharpe_ratio']:+.4f} (Sortino: {ml_perf['sortino_ratio']:+.4f})")
    print(f"ML Cumulative Return:        {ml_perf['cumulative_return']*100:+.2f}% (Max Drawdown: {ml_perf['max_drawdown']*100:.2f}%)")
    print(f"Benchmark SPY Sharpe:        {bm_perf['sharpe_ratio']:+.4f} (Sortino: {bm_perf['sortino_ratio']:+.4f})")
    print(f"Benchmark Cumulative Return: {bm_perf['cumulative_return']*100:+.2f}% (Max Drawdown: {bm_perf['max_drawdown']*100:.2f}%)")
    print("-" * 60)
    print("Rule-Based Strategy Sharpes:")
    for strat, m in rule_metrics.items():
        print(f"  {strat:15s}: Sharpe {m['sharpe_ratio']:+.4f} | Cum Ret {m['cumulative_return']*100:+.2f}% | Max DD {m['max_drawdown']*100:.2f}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
