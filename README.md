# MacroQuant AI — Macroeconomic Intelligence & Strategy Research

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-31%20passed-success.svg)](https://pytest.org/)
[![Lint](https://img.shields.io/badge/ruff-passing-brightgreen.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit UI](https://img.shields.io/badge/Streamlit-Interactive%20UI-FF4B4B.svg)](https://streamlit.io/)

MacroQuant AI is a modular quantitative research framework designed to analyze macroeconomic disclosures, central bank policy announcements, and quantitative trading strategies.

The repository includes live multi-source data ingestion (Apify, Tavily, Exa), a real 180-day historical macroeconomic backfill, genuine historical market backtesting on real S&P 500 daily price data (SPY via Yahoo Finance), leakage-safe walk-forward validation with realistic transaction costs (2 bps), and an interactive Streamlit research dashboard.

---

## Dashboard Preview

The MacroQuant AI interactive research dashboard is built with Streamlit and Plotly, providing real-time data exploration, macro sentiment analytics, genuine historical market backtesting, and machine learning model validation.

### 1. Research Overview
![Research Overview](docs/screenshots/01_research_overview.png)
*Figure 1: Research Overview view displaying high-level system metrics, active strategy counts, verified data points, and pipeline execution status.*

The **Research Overview** tab provides a consolidated executive summary across the entire quantitative pipeline:
- **Core System Metrics:** Highlights the **169 real macroeconomic events** ingested across the 180-day horizon, **39 verified financial news documents**, **257 days of real SPY market prices**, and the **+0.3713 out-of-sample Sharpe ratio** achieved by the dynamic ML strategy.
- **Pipeline Status Cards:** Confirms active status across Live Data Ingestion (Apify `scrapers_lat~economic-calendar-scraper`, Tavily, Exa), Market Backtest Engine (SPY, 246 trading sessions), and Model Validation (3-fold chronological walk-forward evaluation).
- **Interactive Surprise Breakdown:** Visualizes real indicator surprises ($actual - forecast$) across global economies.

---

### 2. Live Intelligence (Real Data)
![Live Intelligence](docs/screenshots/02_live_intelligence.png)
*Figure 2: Live Intelligence view showing real macroeconomic calendar surprises, news sentiment distribution, and primary central bank sources.*

The **Live Intelligence** tab displays verified real-world disclosures collected via the live ingestion pipeline:
- **180-Day Historical Backfill:** Explores **169 verified economic events** spanning April 15, 2026 to October 8, 2026 across 19 countries (UK, Germany, India, France, Japan, US, etc.).
- **Interactive Filtering:** Filter economic events and news by country, event impact level (High, Medium, Low), and provider.
- **Economic Calendar Surprises:** Tabulates actual prints, consensus forecasts, previous values, and computed surprise spreads ($actual - forecast$) without manufactured data.
- **Lexical Sentiment Analytics:** Visualizes the distribution of hawkish (+), neutral (0), and dovish (-) financial news tone scores across verified articles.
- **Primary Source Citations:** Provides clickable links to verified releases from the Federal Reserve Board, Bureau of Labor Statistics, New York Fed, and CNBC.

---

### 3. Macro Events Explorer (Demo)
![Macro Events](docs/screenshots/03_macro_events.png)
*Figure 3: Macro Events view showcasing historical event frequency, surprise spreads, and interactive indicator selection.*

The **Macro Events** tab explores the 180-day baseline macroeconomic disclosure dataset:
- **Event Breakdown:** Analyzes 180 historical disclosures across 6 core indicators: CPI, FOMC, GDP, NFP, Retail Sales, and PMI.
- **Surprise Distribution Histogram:** Displays the statistical distribution of standardized indicator surprises ($Z$-scores) with a zero-reference mean line.
- **Detailed Historical Ledger:** Provides an interactive data table with release timestamps, consensus surveys, and revision history.

---

### 4. Strategy Lab
![Strategy Lab](docs/screenshots/04_strategy_lab.png)
*Figure 4: Strategy Lab view visualizing cumulative returns across parameter variations with transaction cost modeling.*

The **Strategy Lab** tab enables interactive quantitative strategy simulation and sensitivity analysis:
- **Dual Backtest Engine Selector:** Toggle between **Genuine SPY Historical Market Backtest (Real Data)** and **Synthetic Baseline Permutations (Demo Data)**.
- **Real Market Backtest Performance:** Visualizes the actual SPY daily price trajectory ($500+ to $778+) and displays performance metrics across 5 algorithmic strategies: Buy & Hold SPY (Sharpe +1.4702), Macro Shock (Sharpe +0.0090), Momentum 5d, Momentum 10d, and Mean Reversion 5d.
- **Friction-Adjusted Analytics:** Evaluates cumulative return, annualized Sharpe ratio, and maximum drawdown with realistic 2 bps transaction fees per trade turnover.

---

### 5. Model Evaluation
![Model Evaluation](docs/screenshots/05_model_evaluation.png)
*Figure 5: Model Evaluation view presenting walk-forward validation folds, out-of-sample return trajectories, and benchmark comparisons.*

The **Model Evaluation** tab presents empirical results from expanding-window walk-forward validation:
- **Genuine Market Evaluation Track:** Evaluates the machine learning dynamic strategy selector against the Buy & Hold SPY benchmark across **123 out-of-sample trading days** (3 expanding folds, April–October 2026):
  * **ML Dynamic Strategy:** Cumulative Return: **+1.86%**, Sharpe: **+0.3713**, Sortino: **+0.6605**, Max Drawdown: **-6.50%**.
  * **Benchmark (Buy & Hold SPY):** Cumulative Return: **+11.80%**, Sharpe: **+1.9605**, Sortino: **+3.1629**, Max Drawdown: **-4.49%**.
- **Fold-by-Fold Breakdown Table:** Documents individual fold metrics (Fold 1: -2.95%, Fold 2: +6.37%, Fold 3: -1.33%).
- **Out-of-Sample Wealth Growth Curve:** Plots daily out-of-sample portfolio growth of $1.00 comparing active ML dynamic allocation against the benchmark index.
- **Synthetic Baseline Demonstration Track:** Documents the parallel Monte Carlo white-noise evaluation (Sharpe -1.011) confirming the absence of lookahead leakage.

---

## Project Architecture

```
MacroQuant-AI/
├── .env.example                  # Template for API credentials (Apify, Tavily, Exa)
├── requirements.txt              # Production and research Python dependencies
├── docs/
│   └── screenshots/              # High-resolution dashboard view captures
│       ├── 01_research_overview.png
│       ├── 02_live_intelligence.png
│       ├── 03_macro_events.png
│       ├── 04_strategy_lab.png
│       └── 05_model_evaluation.png
├── scripts/
│   ├── backfill_macro_events.py  # 180-day real macro calendar backfill CLI (Apify, 18 intervals)
│   ├── refresh_macro_news.py     # Live multi-query news refresh CLI (Tavily, Exa)
│   ├── run_market_backtest.py    # Genuine historical market backtest driver (SPY, Yahoo Finance)
│   ├── build_pipeline.py         # End-to-end real data pipeline & macro outlook generator
│   ├── generate_sample_data.py   # Reproducible synthetic macro event generator (180 days)
│   ├── ingest_real_data.py       # Single-provider live API ingestion CLI driver
│   └── take_dashboard_screenshots.py # Playwright UI screenshot automation
├── src/
│   ├── backtesting/
│   │   ├── __init__.py
│   │   └── market_backtest.py    # Real market backtest engine (SPY, alignment, walk-forward, 2 bps fees)
│   ├── ingestion/
│   │   ├── clients.py            # API clients with timeouts, retries, and data sanitization
│   │   └── pipeline.py           # Multi-provider data integration & lexical sentiment analysis
│   ├── features/
│   │   └── build_features.py     # Expanding-window feature engineering (leakage-safe)
│   ├── models/
│   │   ├── build_strategy_dataset.py # Strategy dataset generator with transaction frictions
│   │   └── train_model.py        # Expanding walk-forward validation & Random Forest regressor
│   └── dashboard/
│       └── app.py                # Streamlit quantitative intelligence & dual-track strategy lab UI
├── reports/
│   ├── macro_coverage_report.md  # Detailed 180-day real macro coverage & provenance report
│   ├── evaluation_report.md      # Comprehensive model evaluation report (Real SPY + Synthetic)
│   ├── macro_outlook.md          # Primary source-backed macroeconomic intelligence report
│   ├── market_backtest_evaluation.json # Machine-readable metrics for genuine SPY market backtest
│   ├── market_backtest_predictions.csv # Out-of-sample daily predictions on real SPY data
│   ├── model_evaluation.json     # Synthetic baseline model evaluation metrics
│   └── walk_forward_predictions.csv # Synthetic baseline out-of-sample prediction logs
├── data/
│   ├── processed/
│   │   ├── real_macro_events.csv # 169 verified real calendar events (180-day backfill)
│   │   ├── real_macro_news.csv   # 39 verified real financial news articles
│   │   └── market_prices.csv     # 257 daily OHLCV bars for SPY (Yahoo Finance)
│   └── raw/
│       └── macro_events.csv      # Synthetic 180-day baseline dataset
└── tests/
    ├── test_data_generation.py   # Synthetic data integrity tests
    ├── test_strategy_dataset.py  # Strategy permutation & target validation tests
    ├── test_train_model.py       # Walk-forward validation & metric calculation tests
    ├── test_ingestion_clients.py # Ingestion client regression tests (sanitization, schema handling)
    └── test_market_backtest.py   # Genuine market backtest unit & regression tests (31 tests total)
```

---

## Data Provenance & Scope

The repository maintains an explicit boundary between verified real external data and synthetic research data:

| Component | Source / Provider | Scope | Verified Status |
| :--- | :--- | :--- | :--- |
| **SPY Market Prices** | Yahoo Finance (`yfinance`) | 246 trading sessions (1 Year) | Verified live daily OHLCV; genuine equity benchmark |
| **Economic Calendar** | Apify (`scrapers_lat~economic-calendar-scraper`) | 180-day backfill (169 releases across 19 countries) | Verified live across 18 chronological intervals |
| **Financial Search** | Tavily Search API | 20 articles (Fed decisions, BLS releases) | Verified live with full URLs |
| **Neural Web Search** | Exa AI Search API | 20 articles (Governor Waller speech, SEP tables) | Verified live with full extracted text |
| **Macro Events (Demo)** | NumPy synthetic generator | 180-day historical demonstration | Synthetic research demonstration only |
| **Market Returns (Demo)** | NumPy normal distribution (`seed=2026`) | 180-day simulated asset returns | Synthetic Brownian noise; pipeline validation only |

---

## Installation & Setup (macOS / Linux)

Follow these copy-pasteable instructions to set up the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/sahil24302021/MacroQuant-AI.git
cd MacroQuant-AI
```

### 2. Create and Activate a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Credentials

Copy the `.env.example` template to `.env`:

```bash
cp .env.example .env
```

Open `.env` in your text editor and provide your personal API credentials:

```ini
# Apify Economic Calendar Scraper configuration
APIFY_API_TOKEN=your_apify_token_here
APIFY_ACTOR_ID=scrapers_lat~economic-calendar-scraper

# Tavily Search API configuration
TAVILY_API_KEY=your_tavily_key_here

# Exa AI Search API configuration
EXA_API_KEY=your_exa_key_here
```

#### How to Obtain Required Credentials:

- **Apify API Token:**
  1. Register for a free account at [apify.com](https://apify.com/).
  2. Navigate to **Console > Settings > Integrations > API tokens**.
  3. Copy your personal API token and paste it into `APIFY_API_TOKEN`.
  4. The configured actor identifier is `scrapers_lat~economic-calendar-scraper`.
- **Tavily Search API Key:**
  1. Register for a free account at [tavily.com](https://tavily.com/).
  2. Copy your API key from the developer dashboard and paste it into `TAVILY_API_KEY`.
- **Exa AI API Key:**
  1. Register for an account at [exa.ai](https://exa.ai/).
  2. Generate an API key in the Exa dashboard and paste it into `EXA_API_KEY`.

> **CRITICAL SECURITY & SUBMISSION POLICY:**
> - **Never commit `.env` or API credentials to Git.** The `.env` file is permanently ignored in `.gitignore`.
> - Do not post API tokens in GitHub Issues, pull requests, or public README files.
> - For assessment review and grading, submit API keys **strictly through the organizer's explicitly authorized private channel** (such as a secure private form or authorized submission portal).

---

## Running the Pipeline, Backtest & Dashboard

### 1. Execute Real 180-Day Macroeconomic Backfill

Collect 180 days of real economic releases across 18 intervals via the configured Apify actor:

```bash
python scripts/backfill_macro_events.py
```

### 2. Refresh Real Macro News

Collect primary Fed speeches, FOMC projections, and BLS reports via Tavily and Exa:

```bash
python scripts/refresh_macro_news.py
```

### 3. Run Genuine Historical Market Backtest

Download authentic daily price series for SPY (S&P 500 ETF Trust), merge macro surprises and sentiment without lookahead bias, and run expanding walk-forward out-of-sample backtests with 2 bps transaction fees:

```bash
python scripts/run_market_backtest.py
```

### 4. Build End-to-End Pipeline & Reports

Compile processed datasets and generate `reports/macro_outlook.md`:

```bash
python scripts/build_pipeline.py
```

### 5. Launch Research Dashboard

Start the local Streamlit application:

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## Testing & Quality Assurance

Run the complete test suite (31 unit and regression tests, 100% offline, zero live network calls):

```bash
# Run ingestion client regression tests
python -m pytest tests/test_ingestion_clients.py -q

# Run market backtest unit tests
python -m pytest tests/test_market_backtest.py -q

# Run full project test suite (31 tests)
python -m pytest -q
```

Run code style and lint checks with Ruff:

```bash
python -m ruff check src scripts tests
```

Verify Git hygiene:

```bash
git diff --check
```

---

## Submission & Reproducibility

This section outlines all artifacts, entry points, and instructions required for formal assessment evaluation.

### Repository Metadata

- **Repository URL:** [https://github.com/sahil24302021/MacroQuant-AI](https://github.com/sahil24302021/MacroQuant-AI)
- **Primary Branch:** `main`
- **Target OS:** macOS / Linux
- **Python Runtime:** Python 3.10+ (tested on Python 3.14)

### Entry Points Summary

| Component | Path / Command | Description |
| :--- | :--- | :--- |
| **Real Macro Backfill** | `scripts/backfill_macro_events.py` | 180-day macro calendar backfill across 18 chronological intervals via Apify |
| **News Refresh Driver** | `scripts/refresh_macro_news.py` | Multi-query live news ingestion and lexical sentiment analysis (Tavily/Exa) |
| **Market Backtest Driver** | `scripts/run_market_backtest.py` | Genuine SPY historical market backtest with expanding walk-forward validation |
| **End-to-End Pipeline** | `scripts/build_pipeline.py` | Real data processing, lexical sentiment calculation, and report compilation |
| **Sample Data Generator** | `scripts/generate_sample_data.py` | Reproducible 180-day synthetic macro event generator for demo testing |
| **Feature Engineering** | `src/features/build_features.py` | Expanding-window feature extraction (leakage-free) |
| **Dataset Assembly** | `src/models/build_strategy_dataset.py` | Multi-strategy return permutation generator with transaction costs |
| **Model Training** | `src/models/train_model.py` | Chronological walk-forward validation harness and Random Forest regressor |
| **Interactive Dashboard** | `src/dashboard/app.py` | Streamlit research interface (`streamlit run src/dashboard/app.py`) |

### Report Deliverables & Locations

| Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Macro Coverage Report** | `reports/macro_coverage_report.md` | Detailed 180-day real macro coverage, schema breakdown, and Apify provenance |
| **Model Evaluation Report** | `reports/evaluation_report.md` | Dual evaluation report: genuine SPY market backtest vs synthetic demonstration |
| **Macro Outlook Report** | `reports/macro_outlook.md` | Primary source-backed intelligence report synthesizing real calendar events, Fed speeches, and BLS releases |
| **Market Backtest Metrics** | `reports/market_backtest_evaluation.json` | Machine-readable metrics for genuine SPY market backtest (Sharpe, Sortino, Drawdown, folds) |
| **Market Backtest Logs** | `reports/market_backtest_predictions.csv` | Granular daily out-of-sample prediction logs on real SPY market prices |
| **Synthetic Model Metrics** | `reports/model_evaluation.json` | Machine-readable metrics for synthetic baseline Monte Carlo test |
| **Synthetic Predictions** | `reports/walk_forward_predictions.csv` | Daily out-of-sample prediction logs for synthetic baseline model |

### Processed Datasets

| Dataset | Path | Provenance | Description |
| :--- | :--- | :--- | :--- |
| **Real Macro Events** | `data/processed/real_macro_events.csv` | Real (Apify) | 169 verified calendar releases (180-day backfill) with actual, forecast, and surprise values |
| **Real Macro News** | `data/processed/real_macro_news.csv` | Real (Tavily/Exa) | 39 verified articles with extracted text and lexical sentiment scores |
| **Real Market Prices** | `data/processed/market_prices.csv` | Real (Yahoo Finance) | 257 daily OHLCV bars for SPY (SPDR S&P 500 ETF Trust) |
| **Macro Features** | `data/processed/macro_features.csv` | Synthetic Demo | Expanding-window standardized macro indicator surprises |
| **Strategy Dataset** | `data/processed/strategy_dataset.csv` | Synthetic Demo | 1,080 rows (180 days × 6 strategies) with modeled transaction frictions |

### Quick Reproduction Sequence

To reproduce the complete research demonstration from a clean clone:

```bash
# 1. Setup
git clone https://github.com/sahil24302021/MacroQuant-AI.git
cd MacroQuant-AI
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Build real backtest and pipeline
python scripts/backfill_macro_events.py
python scripts/refresh_macro_news.py
python scripts/run_market_backtest.py
python scripts/build_pipeline.py

# 3. Build synthetic demo pipeline (optional for regression testing)
python scripts/generate_sample_data.py
python src/features/build_features.py
python src/models/build_strategy_dataset.py
python src/models/train_model.py

# 4. Verify tests and lint
python -m pytest -q
python -m ruff check src scripts tests

# 5. Launch research dashboard
streamlit run src/dashboard/app.py
```

---

## Explicit Disclosures & Methodological Limitations

To maintain institutional research integrity, the following limitations are explicitly disclosed:

1. **Real Macroeconomic Backfill Scope:**
   - Real macroeconomic calendar ingestion covers **169 unique releases** spanning the 180-day window (2026-04-15 to 2026-10-08) collected across 18 distinct date intervals via Apify Actor `scrapers_lat~economic-calendar-scraper`.
   - Of these 169 events, 66 had published consensus forecasts (37 upside, 26 downside, 3 in-line); releases without forecasts have surprises intentionally recorded as `null` rather than fabricated values.
   - The Apify actor retrieves the first 10 events matching `dateFrom` from Nasdaq without native pagination parameters, which was mitigated by our 18-interval sampling schedule.
2. **Genuine Market Backtest Parameters & Interpretation:**
   - The real market backtest evaluates **SPY (SPDR S&P 500 ETF Trust)** daily price returns from Yahoo Finance across 246 trading sessions, with 123 days evaluated strictly out-of-sample (April–October 2026).
   - The ML dynamic strategy achieved an out-of-sample cumulative return of **+1.86%** (Sharpe **+0.3713**, Sortino **+0.6605**, Max Drawdown **-6.50%**), while passive Buy & Hold SPY returned **+11.80%** (Sharpe **+1.9605**).
   - In a strong trending equity bull market (+11.8%), passive holding naturally outperformed active rebalancing, as active regime switching incurred cash drag and 2 bps transaction fees.
3. **Synthetic Demonstration Datasets:**
   - The 180-day timeline in `data/raw/macro_events.csv` and `data/processed/strategy_dataset.csv` is a **reproducible synthetic demonstration dataset** maintained for pipeline sanity testing and demonstrating that the evaluation harness penalizes overfitting when tested on pure Gaussian white noise (Sharpe -1.011).
4. **Lexical Sentiment Heuristic:**
   - News sentiment scores are derived from transparent financial lexicons (hawkish vs. dovish terms). This is a descriptive tone proxy rather than an econometric alpha forecast.

---

## License

This project is licensed under the [MIT License](LICENSE).
