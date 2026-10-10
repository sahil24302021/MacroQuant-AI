# MacroQuant AI — Macroeconomic Intelligence & Strategy Research

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-26%20passed-success.svg)](https://pytest.org/)
[![Lint](https://img.shields.io/badge/ruff-passing-brightgreen.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit UI](https://img.shields.io/badge/Streamlit-Interactive%20UI-FF4B4B.svg)](https://streamlit.io/)

MacroQuant AI is a modular quantitative research framework designed to analyze macroeconomic disclosures, central bank policy announcements, and quantitative trading strategies.

The repository includes live multi-source data ingestion (Apify, Tavily, Exa), leakage-safe expanding-window feature engineering, chronological walk-forward model evaluation, and an interactive Streamlit research dashboard.

---

## Dashboard Preview

The MacroQuant AI interactive research dashboard is built with Streamlit and Plotly, providing real-time data exploration, macro sentiment analytics, strategy backtesting simulations, and machine learning model validation.

### 1. Research Overview
![Research Overview](docs/screenshots/01_research_overview.png)
*Figure 1: Research Overview view displaying high-level system metrics, active strategy counts, verified data points, and pipeline execution status.*

The **Research Overview** tab provides a consolidated executive summary across the entire quantitative pipeline:
- **Core System Metrics:** Highlights the 180-day research horizon, 6 quantitative strategy variations, 10 verified real calendar events, 20 real financial news documents, and the current Random Forest regressor out-of-sample $R^2$ score.
- **Pipeline Status Cards:** Confirms active status across Data Ingestion (Apify, Tavily, Exa), Feature Engineering (expanding-window z-scores), and Model Validation (3-fold chronological walk-forward evaluation).
- **Architecture Flow:** Outlines the end-to-end data processing lifecycle from raw API ingestion to interactive strategy analytics.

---

### 2. Live Intelligence (Real Data)
![Live Intelligence](docs/screenshots/02_live_intelligence.png)
*Figure 2: Live Intelligence view showing real macroeconomic calendar surprises, news sentiment distribution, and primary central bank sources.*

The **Live Intelligence** tab displays verified real-world disclosures collected via the live ingestion pipeline:
- **Interactive Filtering:** Filter economic events and news by country (Australia, Japan, United States, etc.), event impact level, and ingestion provider.
- **Economic Calendar Surprises:** Tabulates actual prints, consensus forecasts, previous values, and computed surprise spreads ($actual - forecast$) without manufactured data.
- **Lexical Sentiment Analytics:** Visualizes the distribution of hawkish (+), neutral (0), and dovish (-) financial news tone scores across 20 verified articles.
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
- **Strategy Permutations:** Compares 6 algorithmic strategies combining trend-following momentum and mean-reversion rules across multiple lookback windows (5-day, 10-day, 20-day).
- **Cumulative Performance Curves:** Visualizes the simulated growth of a \$1.00 portfolio over time across all strategy configurations.
- **Friction-Adjusted Analytics:** Evaluates cumulative return, annualized Sharpe ratio, and maximum drawdown with realistic 2 bps transaction fees per trade.

---

### 5. Model Evaluation
![Model Evaluation](docs/screenshots/05_model_evaluation.png)
*Figure 5: Model Evaluation view presenting walk-forward validation folds, out-of-sample return trajectories, and benchmark comparisons.*

The **Model Evaluation** tab presents empirical results from expanding-window walk-forward validation:
- **Leakage-Safe Validation Scheme:** Details partition boundaries across 3 sequential folds (Day 0–90 initial train partition, Days 90–180 out-of-sample evaluation).
- **Ensemble vs. Baseline Comparison:** Evaluates the machine learning dynamic strategy selector against the single best in-sample baseline (`momentum`), displaying Sharpe ratio (-1.011 vs. +0.246), Sortino ratio (-1.343 vs. +0.334), Maximum Drawdown (-10.19% vs. -9.14%), and cumulative return (-6.17% vs. +0.88%).
- **Out-of-Sample Performance Curve:** Plots daily out-of-sample portfolio trajectories and documents fold-by-fold validation performance metrics.

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
│   ├── generate_sample_data.py   # Reproducible synthetic macro event generator (180 days)
│   ├── ingest_real_data.py       # Live API ingestion CLI driver (Apify, Tavily, Exa)
│   ├── build_pipeline.py         # Real data processing & macro outlook generator
│   └── take_dashboard_screenshots.py # Playwright UI screenshot automation
├── src/
│   ├── ingestion/
│   │   ├── clients.py            # API clients with timeouts, retries, and data sanitization
│   │   └── pipeline.py           # Multi-provider data integration & lexical sentiment analysis
│   ├── features/
│   │   └── build_features.py     # Expanding-window feature engineering (leakage-safe)
│   ├── models/
│   │   ├── build_strategy_dataset.py # Strategy dataset generator with transaction frictions
│   │   └── train_model.py        # Expanding walk-forward validation & Random Forest regressor
│   └── dashboard/
│       └── app.py                # Streamlit quantitative intelligence & strategy lab UI
├── reports/
│   ├── macro_outlook.md          # Primary source-backed macroeconomic intelligence report
│   ├── evaluation_report.md      # Walk-forward model evaluation & benchmark comparison
│   ├── model_evaluation.json     # Machine-readable performance metrics
│   └── walk_forward_predictions.csv # Out-of-sample prediction logs
└── tests/
    ├── test_data_generation.py   # Synthetic data integrity tests
    ├── test_strategy_dataset.py  # Strategy permutation & target validation tests
    ├── test_train_model.py       # Walk-forward validation & metric calculation tests
    └── test_ingestion_clients.py # Ingestion client regression tests (sanitization, schema handling)
```

---

## Data Provenance & Scope

The repository maintains an explicit boundary between verified real external data and synthetic research data:

| Component | Source / Provider | Scope | Verified Status |
| :--- | :--- | :--- | :--- |
| **Economic Calendar** | Apify (`scrapers_lat~economic-calendar-scraper`) | 7-day test slice (10 releases) | Verified live; full 180-day backfill is a planned batch task |
| **Financial Search** | Tavily Search API | 10 articles (Fed speeches, BLS portal) | Verified live |
| **Neural Web Search** | Exa AI Search API | 10 articles (Governor Waller speech, SEP tables) | Verified live with full extracted text |
| **Macro Events (Demo)** | NumPy synthetic generator | 180-day historical demonstration | Synthetic research demonstration only |
| **Market Returns** | NumPy normal distribution (`seed=2026`) | 180-day simulated asset returns | Synthetic Brownian noise; not real trade PnL |

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

## Running the Pipeline & Dashboard

### 1. Dry-Run Verification (Free, Offline)

Verify that the ingestion clients and schema sanitizers work without making external network calls:

```bash
python scripts/ingest_real_data.py --provider tavily
python scripts/ingest_real_data.py --provider exa
python scripts/ingest_real_data.py --provider apify
```

### 2. Run Sample Data Pipeline

Generate the 180-day baseline synthetic research dataset and compute features:

```bash
python scripts/generate_sample_data.py
python src/features/build_features.py
python src/models/build_strategy_dataset.py
python src/models/train_model.py
```

### 3. Process Real Ingested Data & Generate Reports

Execute the integration pipeline to sanitize ingested records, compute macro sentiment, and compile `reports/macro_outlook.md`:

```bash
python scripts/build_pipeline.py
```

### 4. Optional: Live Data Ingestion

If valid credentials are configured in `.env`, run live queries:

```bash
# Ingest recent financial news via Tavily
python scripts/ingest_real_data.py --provider tavily --live

# Ingest recent central bank disclosures via Exa
python scripts/ingest_real_data.py --provider exa --live

# Ingest economic calendar events (7-day test slice) via Apify
python scripts/ingest_real_data.py --provider apify --days 7 --live
```

### 5. Launch Research Dashboard

Start the local Streamlit application:

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## Testing & Quality Assurance

Run the test suite (26 unit and regression tests, 100% offline, zero live network calls):

```bash
# Run ingestion client regression tests
python -m pytest tests/test_ingestion_clients.py -q

# Run full project test suite
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
| **CLI Ingestion Driver** | `scripts/ingest_real_data.py` | Command-line interface for dry-run and live multi-provider ingestion |
| **End-to-End Pipeline** | `scripts/build_pipeline.py` | Real data processing, lexical sentiment calculation, and report compilation |
| **Sample Data Generator** | `scripts/generate_sample_data.py` | Reproducible 180-day synthetic macro event generator |
| **Feature Engineering** | `src/features/build_features.py` | Expanding-window feature extraction (leakage-free) |
| **Dataset Assembly** | `src/models/build_strategy_dataset.py` | Multi-strategy return permutation generator with transaction costs |
| **Model Training** | `src/models/train_model.py` | Chronological walk-forward validation harness and Random Forest regressor |
| **Interactive Dashboard** | `src/dashboard/app.py` | Streamlit research interface (`streamlit run src/dashboard/app.py`) |

### Report Deliverables & Locations

| Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Macro Outlook Report** | `reports/macro_outlook.md` | Primary source-backed intelligence report synthesizing real calendar events, Fed speeches, and BLS releases |
| **Model Evaluation Report** | `reports/evaluation_report.md` | Formal walk-forward model evaluation report comparing ML ensemble to static baseline |
| **Model Evaluation Metrics** | `reports/model_evaluation.json` | Machine-readable JSON metrics (Sharpe, Sortino, Drawdown, cumulative return, per-fold stats) |
| **Out-of-Sample Predictions** | `reports/walk_forward_predictions.csv` | Granular daily out-of-sample prediction logs generated by walk-forward folds |

### Processed Datasets

| Dataset | Path | Provenance | Description |
| :--- | :--- | :--- | :--- |
| **Real Macro Events** | `data/processed/real_macro_events.csv` | Real (Apify) | Sanitized 7-day calendar releases with actual, forecast, and surprise values |
| **Real Macro News** | `data/processed/real_macro_news.csv` | Real (Tavily/Exa) | 20 verified articles with extracted text and lexical sentiment scores |
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

# 2. Build demo pipeline
python scripts/generate_sample_data.py
python src/features/build_features.py
python src/models/build_strategy_dataset.py
python src/models/train_model.py
python scripts/build_pipeline.py

# 3. Verify tests and lint
python -m pytest -q
python -m ruff check src scripts tests

# 4. Launch research dashboard
streamlit run src/dashboard/app.py
```

---

## Explicit Disclosures & Methodological Limitations

To maintain institutional research integrity, the following limitations are explicitly disclosed:

1. **Live Calendar Scope (7-Day Slice vs. 180-Day Backfill):**
   - Live calendar ingestion currently covers a **verified 7-day test slice (10 events)** collected via Apify Actor `scrapers_lat~economic-calendar-scraper`.
   - Of these 10 events, exactly 5 had published consensus forecasts (3 surprised upside, 2 downside); releases without forecasts have surprises intentionally recorded as `null` rather than fabricated values.
   - A full 180-day historical calendar backfill has **not** been completed and remains a planned future batch task requiring multi-interval actor queries.
2. **Synthetic Demonstration Datasets:**
   - The 180-day timeline in `data/raw/macro_events.csv` and `data/processed/strategy_dataset.csv` is a **reproducible synthetic demonstration dataset** designed to validate pipeline architecture, leak-free feature pipelines, and expanding-window validation code.
3. **Synthetic Market Returns & Performance Metrics:**
   - Asset returns in the Strategy Lab and Model Evaluation are generated via **simulated Gaussian white noise (Brownian motion, `seed=2026`)**.
   - Model performance metrics (e.g., ensemble Sharpe ratio of -1.011, cumulative return of -6.17%) reflect **machine learning evaluation mechanics on synthetic noise**, NOT evidence of a genuine historical market-price backtest or live trading profitability.
   - Do not interpret strategy performance figures as commercial or real-world trading results.
4. **Lexical Sentiment Heuristic:**
   - News sentiment scores are derived from transparent financial lexicons (hawkish vs. dovish terms). This is a descriptive tone proxy rather than an econometric alpha forecast.
5. **Future Roadmap:**
   - Ingest genuine high-frequency market prices (e.g., SPY, TLT, DXY) for authentic post-announcement price discovery backtesting.
   - Integrate transformer-based domain embeddings (FinBERT) for contextual sentiment extraction.

---

## License

This project is licensed under the [MIT License](LICENSE).
