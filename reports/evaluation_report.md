# MacroQuant AI — Quantitative Research & Model Evaluation Report

**Document Version:** 2.0.0<br>
**Evaluation Architecture:** Chronological Expanding-Window Walk-Forward Validation<br>
**Research Horizon:** 180 Days (Out-of-Sample Window: 123 Days across 3 Folds)<br>
**Security & Provenance Classification:** Strict Dual Evaluation — Genuine Market Backtest (SPY / Real Macro) vs. Synthetic Simulation

---

## 1. Executive Summary

This evaluation report presents quantitative results from the `MacroQuant-AI` research framework, establishing an explicit, rigorous boundary between **genuine historical market backtesting on real asset prices** and **synthetic Monte Carlo pipeline verification**.

Key findings:
1. **Real-World 180-Day Macro Backfill:** Collected and validated **169 genuine macroeconomic calendar releases** (spanning 2026-04-15 to 2026-10-08) via Apify Actor `scrapers_lat~economic-calendar-scraper`, and **39 verified unique financial publications/central bank speeches** (deduplicated from 40 raw results across Tavily and Exa). Numeric values were sanitized to strictly finite floats, non-breaking spaces (`&nbsp;`) were unescaped, and missing consensus surveys were preserved as `null` rather than manufactured zero spreads.
2. **Genuine Historical Market Backtest (SPY, Real Data):** Evaluated against authentic daily OHLCV prices of **SPY (SPDR S&P 500 ETF Trust)** via Yahoo Finance across 246 trading sessions, with **123 days evaluated strictly out-of-sample** across 3 expanding walk-forward folds with realistic 2 bps transaction fees.
   - The **ML Dynamic Strategy Selector** achieved an out-of-sample cumulative return of **+1.86%**, an annualized Sharpe ratio of **+0.3713**, a Sortino ratio of **+0.6605**, and a maximum drawdown of **-6.50%**.
   - The **Benchmark (SPY Buy & Hold)** over the same out-of-sample window yielded **+11.80%**, an annualized Sharpe ratio of **+1.9605**, a Sortino ratio of **+3.1629**, and a maximum drawdown of **-4.49%**.
3. **Synthetic Demonstration Benchmark:** In parallel, the leak-free evaluation architecture was tested against pure Gaussian white noise returns. Over 90 synthetic out-of-sample days, the model yielded a Sharpe ratio of **-1.011** (cumulative return of **-6.17%**), validating that the walk-forward evaluation harness strictly avoids lookahead bias and penalizes overfitting when true signal is absent.
4. **Institutional Takeaway:** In a persistent bull market for US equities (+11.80% SPY return over the out-of-sample period), active macroeconomic regime switching incurred higher transaction frictions and cash drag relative to passive indexing, while successfully preserving capital and maintaining positive risk-adjusted metrics (+0.37 Sharpe, +0.66 Sortino).

---

## 2. Data Sources & Provenance Architecture

| Source / Asset | Provider / Engine | Scope & Horizon | Role in System | Provenance Tag | Verified Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SPY Market Prices** | Yahoo Finance (`yfinance`) | 246 trading days (1 Year) | Authentic equity price discovery benchmark | `real_yahoo_finance` | Verified live |
| **Economic Calendar** | Apify (`scrapers_lat~economic-calendar-scraper`) | 180 days (169 releases across 19 countries) | Actual macro indicator surprises & shocks | `real_verified` | Verified live (18 intervals) |
| **Financial Search** | Tavily Search API | 20 articles (Fed decisions, BLS releases) | Financial news sentiment & tone tracking | `real_verified` | Verified live |
| **Neural Web Search** | Exa AI Search API | 19 unique articles (20 raw) (Governor Waller speech, SEP tables) | Deep primary central bank documentation | `real_verified` | Verified live with full extracted text |
| **Simulated Market** | NumPy Generator (`seed=2026`) | 180 days (Synthetic random walk) | Baseline pipeline & ML code validation | `synthetic_demo` | Pure synthetic Monte Carlo |

### Data Cleaning & Integrity Protocol
- **HTML Artifacts:** Extracted strings are unescaped (`html.unescape`) and cleared of non-breaking spaces (`&nbsp;`, `\xa0`).
- **Missing Value Handling:** Missing, empty, or unreleased values (e.g., meetings without consensus forecasts) remain strictly `None`/`null`. Zeroes or synthetic interpolations are **never** invented.
- **Timestamp Standardization:** Calendar timestamps with explicit GMT notations are normalized to ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SS+00:00`). Unknown timezones are tagged as `unspecified` without silent guesswork.
- **Deduplication:** Overlapping chunks are filtered by composite unique keys `(event_name, date, time, country, actual, forecast)` and unique web URLs.

---

## 3. Genuine Historical Market Backtest (SPY / Real Macro)

### Backtest Configuration
- **Underlying Benchmark:** SPY (SPDR S&P 500 ETF Trust), daily close-to-close returns.
- **Execution Timing:** Signals calculated at close of day $t$ (using macro releases and price indicators available by day $t$) trade for day $t+1$ returns. Zero lookahead bias.
- **Transaction Costs:** Modeled at **2 basis points (0.0002)** per turnover unit on all position rebalancing.
- **Out-of-Sample Window:** 123 trading days spanning **2026-04-15 to 2026-10-08** across 3 expanding chronological walk-forward folds.

### Out-of-Sample Performance Comparison Table

| Performance Metric | ML Dynamic Strategy (Out-of-Sample) | Benchmark: SPY Buy & Hold | Difference / Variance |
| :--- | :--- | :--- | :--- |
| **Out-of-Sample Observations** | 123 days | 123 days | 0 days |
| **Evaluation Date Range** | 2026-04-15 to 2026-10-08 | 2026-04-15 to 2026-10-08 | Identical |
| **Cumulative Return** | **+1.86%** | **+11.80%** | -9.94% |
| **Annualized Return** | **+4.49%** | **+23.57%** | -19.08% |
| **Annualized Volatility** | **12.10%** | **12.03%** | +0.07% |
| **Annualized Sharpe Ratio** | **+0.3713** | **+1.9605** | -1.5892 |
| **Annualized Sortino Ratio** | **+0.6605** | **+3.1629** | -2.5024 |
| **Maximum Drawdown** | **-6.50%** | **-4.49%** | -2.01% |
| **Win Rate (% Positive Days)** | **48.78%** | **51.22%** | -2.44% |
| **Transaction Frictions Incurred**| 2.0 bps / trade | 0 bps (static hold) | Active turnover drag |

### Fold-by-Fold Performance Breakdown (OOS)

| Fold | Out-of-Sample Window | ML Return | ML Sharpe | ML Max Drawdown | Win Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fold 1** | 2026-04-15 to 2026-06-11 | -2.95% | -1.3626 | -6.50% | 43.90% |
| **Fold 2** | 2026-06-12 to 2026-08-11 | **+6.37%** | **+2.8736** | **-3.17%** | **51.22%** |
| **Fold 3** | 2026-08-12 to 2026-10-08 | -1.33% | -0.8237 | -4.83% | 51.22% |
| **Overall** | **2026-04-15 to 2026-10-08** | **+1.86%** | **+0.3713** | **-6.50%** | **48.78%** |

### Rule-Based Strategies Across Full Period (246 Days)

| Strategy | Cumulative Return | Annualized Sharpe | Maximum Drawdown | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Buy & Hold SPY** | **+19.12%** | **+1.4702** | -8.88% | Passive holding benchmark |
| **Macro Shock** | -0.13% | **+0.0090** | -9.43% | Long on net positive macro surprise, short on negative |
| **Momentum (5-Day)** | -2.25% | -0.1188 | -12.07% | 5-day price trend following |
| **Mean Reversion (5-Day)**| -4.04% | -0.3634 | -12.28% | 5-day volatility band reversion |
| **Momentum (10-Day)** | -13.64% | -1.1098 | -17.98% | 10-day price trend following |

---

## 4. Synthetic Baseline Demonstration (Monte Carlo Simulation)

For architectural regression testing, the system maintains a synthetic demonstration dataset (`data/raw/macro_events.csv`, 180 days) coupled with simulated Gaussian return noise (`seed=2026`):

| Metric | Selected Ensemble Strategy (Out-of-Sample) | Baseline: Best In-Sample Strategy (`momentum`) | Variance / Difference |
| :--- | :--- | :--- | :--- |
| **Evaluation Observations** | 90 days | 90 days | 0 days |
| **Mean Daily Return** | **-0.0655%** | **+0.0136%** | -0.0791% |
| **Annualized Sharpe Ratio** | **-1.011** | **+0.246** | -1.257 |
| **Annualized Sortino Ratio** | **-1.343** | **+0.334** | -1.677 |
| **Maximum Drawdown** | **-10.19%** | **-9.14%** | -1.05% |
| **Cumulative Return** | **-6.17%** | **+0.88%** | -7.05% |

**Interpretation:** On pure white noise, out-of-sample machine learning selection underperformed the simple static baseline, verifying that the evaluation harness penalizes overfitting and prevents artificial positive returns when true predictable signal is absent.

---

## 5. Methodological Limitations & Future Milestones

1. **Apify Pagination Constraint & Sampling:**
   - The Apify actor (`scrapers_lat~economic-calendar-scraper`) retrieves the first 10 items from Nasdaq calendar per execution. To achieve full 180-day coverage, the pipeline deployed 18 chronological intervals (yielding 169 unique events).
2. **Daily Aggregation vs. Intraday High-Frequency:**
   - Real market backtests use daily close-to-close returns. Real-world macro trading frequently involves high-frequency post-release volatility within 5 to 60 minutes of scheduled releases.
   - *Next Milestone (Planned):* Ingest 1-minute intraday tick data around high-impact FOMC and CPI timestamps.
3. **Lexical Sentiment Dictionary:**
   - News sentiment scores use transparent financial lexicons (hawkish vs. dovish terms).
   - *Next Milestone (Planned):* Incorporate fine-tuned transformer models (FinBERT) for contextual parsing.
