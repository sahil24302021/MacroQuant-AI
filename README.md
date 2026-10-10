# MacroQuant AI — Macroeconomic Intelligence & Strategy Research

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/pytest-26%20passed-success.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MacroQuant AI is a modular quantitative research framework designed to analyze macroeconomic disclosures, central bank policy announcements, and quantitative trading strategies.

The repository includes live multi-source data ingestion (Apify, Tavily, Exa), leakage-safe feature engineering, expanding-window walk-forward model evaluation, and an interactive Streamlit research dashboard.

---

## Project Architecture

```
MacroQuant-AI/
├── .env.example                  # Template for API credentials (Apify, Tavily, Exa)
├── requirements.txt              # Production and research Python dependencies
├── scripts/
│   ├── generate_sample_data.py   # Reproducible synthetic macro event generator (180 days)
│   ├── ingest_real_data.py       # Live API ingestion CLI driver (Apify, Tavily, Exa)
│   └── build_pipeline.py         # Real data processing & macro outlook generator
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
| **Economic Calendar** | Apify (`scrapers_lat~economic-calendar-scraper`) | 7-day test slice (10 releases) | Verified live; full 180-day backfill is planned |
| **Financial Search** | Tavily Search API | 10 articles (Fed speeches, BLS portal) | Verified live |
| **Neural Web Search** | Exa AI Search API | 10 articles (Governor Waller speech, SEP tables) | Verified live with full extracted text |
| **Macro Events (Demo)** | NumPy synthetic generator | 180-day historical demonstration | Synthetic research demonstration only |
| **Market Returns** | NumPy normal distribution (`seed=2026`) | 180-day simulated asset returns | Synthetic Brownian noise; not real trade PnL |

---

## Quickstart & Setup

### 1. Environment Setup

Create or activate the virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example environment file and insert your API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your provider keys:

```ini
APIFY_API_TOKEN=your_apify_token_here
APIFY_ACTOR_ID=scrapers_lat~economic-calendar-scraper
TAVILY_API_KEY=your_tavily_key_here
EXA_API_KEY=your_exa_key_here
```

> **Security Note:** Real API keys are never printed, logged, or checked into version control. The `.env` file and `data/raw/*.json` are explicitly ignored in `.gitignore`.

---

## Data Ingestion & Pipeline

### Dry-Run Verification (Free, Offline)

Verify ingestion client drivers offline without making live API requests:

```bash
python scripts/ingest_real_data.py --provider tavily
python scripts/ingest_real_data.py --provider exa
python scripts/ingest_real_data.py --provider apify
```

### Live Ingestion

To execute targeted live API queries:

```bash
# Ingest recent financial news via Tavily
python scripts/ingest_real_data.py --provider tavily --live

# Ingest recent financial news with neural text extraction via Exa
python scripts/ingest_real_data.py --provider exa --live

# Ingest recent economic calendar events (e.g., 7-day slice) via Apify
python scripts/ingest_real_data.py --provider apify --days 7 --live
```

### End-to-End Real Data Processing

Process ingested raw records, sanitize HTML entities, compute lexical macro sentiment, and generate the Macro Outlook report:

```bash
python scripts/build_pipeline.py
```

---

## Testing & Code Quality

Run the complete test suite (26 unit and regression tests, zero live network calls):

```bash
# Test ingestion clients and sanitization
python -m pytest tests/test_ingestion_clients.py -q

# Run full project test suite (26 tests)
python -m pytest -q
```

Linting and code style verification:

```bash
python -m ruff check src scripts tests
```

---

## Research Dashboard

Launch the interactive Streamlit research dashboard:

```bash
streamlit run src/dashboard/app.py
```

Dashboard tabs:
1. **Research Overview:** High-level metrics comparing verified live intelligence against demonstration datasets.
2. **Live Intelligence (Real Data):** Real calendar releases, actual-vs-forecast surprises, and news sentiment distributions.
3. **Macro Events (Demo):** Synthetic data explorer with interactive surprise distribution plots.
4. **Strategy Lab:** Strategy performance curves across momentum and mean-reversion parameter variations.
5. **Model Evaluation:** Walk-forward out-of-sample metrics (Sharpe, Sortino, Max Drawdown) compared to benchmark.

---

## Methodology & Limitations

1. **Synthetic Market Returns:** While macroeconomic indicators and news documents reflect verified real-world sources, market returns in the Strategy Lab are generated via a normal random distribution. Walk-forward performance reflects machine learning evaluation mechanics, not live market profitability.
2. **Live Calendar Scope:** Live Apify ingestion currently covers a verified 7-day test slice. Full 180-day historical calendar backfill is planned as a future batch task requiring multi-interval actor runs.
3. **Lexical Sentiment Heuristic:** News sentiment is evaluated via keyword frequency matching against curated financial lexicons. It provides a descriptive tone metric rather than a directional price forecast.
4. **Planned Extensions:** Ingesting historical market price series (e.g., SPY, TLT) for genuine price discovery backtesting, and integrating fine-tuned transformer embeddings (FinBERT).
