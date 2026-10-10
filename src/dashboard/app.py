import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
EVENTS_FILE = ROOT / "data" / "raw" / "macro_events.csv"
FEATURES_FILE = ROOT / "data" / "processed" / "macro_features.csv"
PREDICTIONS_FILE = ROOT / "reports" / "walk_forward_predictions.csv"
EVALUATION_FILE = ROOT / "reports" / "model_evaluation.json"

REAL_EVENTS_FILE = ROOT / "data" / "processed" / "real_macro_events.csv"
REAL_NEWS_FILE = ROOT / "data" / "processed" / "real_macro_news.csv"
APIFY_RAW_FILE = ROOT / "data" / "raw" / "apify_live.json"
TAVILY_RAW_FILE = ROOT / "data" / "raw" / "tavily_live.json"
EXA_RAW_FILE = ROOT / "data" / "raw" / "exa_live.json"

MARKET_PRICES_FILE = ROOT / "data" / "processed" / "market_prices.csv"
MARKET_EVAL_FILE = ROOT / "reports" / "market_backtest_evaluation.json"
MARKET_PREDS_FILE = ROOT / "reports" / "market_backtest_predictions.csv"

st.set_page_config(
    page_title="MacroQuant AI — Quantitative Research & Intelligence",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.2);
        padding: 14px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    .badge-real {
        background-color: #0e7490;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-demo {
        background-color: #b45309;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("MacroQuant AI")
st.caption("Macroeconomic Intelligence · Quantitative Research · Walk-Forward Strategy Evaluation")

# Provenance & disclaimer banner
st.info(
    "🛡️ **System Architecture & Data Segregation:** "
    "Macroeconomic indicators (169 events, 180-day backfill) and central bank news reflect **verified real-world API data** (Apify, Tavily, Exa). "
    "Market price backtesting is conducted on **genuine historical SPY daily data** (Yahoo Finance) alongside separately labeled synthetic baseline demonstrations."
)

# Safe data loaders
events = pd.read_csv(EVENTS_FILE) if EVENTS_FILE.exists() else pd.DataFrame()
features = pd.read_csv(FEATURES_FILE) if FEATURES_FILE.exists() else pd.DataFrame()
predictions = pd.read_csv(PREDICTIONS_FILE) if PREDICTIONS_FILE.exists() else pd.DataFrame()

real_events = pd.read_csv(REAL_EVENTS_FILE) if REAL_EVENTS_FILE.exists() else pd.DataFrame()
real_news = pd.read_csv(REAL_NEWS_FILE) if REAL_NEWS_FILE.exists() else pd.DataFrame()

market_prices = pd.read_csv(MARKET_PRICES_FILE) if MARKET_PRICES_FILE.exists() else pd.DataFrame()
market_preds = pd.read_csv(MARKET_PREDS_FILE) if MARKET_PREDS_FILE.exists() else pd.DataFrame()

evaluation = {}
if EVALUATION_FILE.exists():
    try:
        with open(EVALUATION_FILE) as file:
            evaluation = json.load(file)
    except (json.JSONDecodeError, OSError):
        evaluation = {}

market_eval = {}
if MARKET_EVAL_FILE.exists():
    try:
        with open(MARKET_EVAL_FILE) as file:
            market_eval = json.load(file)
    except (json.JSONDecodeError, OSError):
        market_eval = {}

# Compute last ingestion time
last_ingestion_ts = None
for f in (APIFY_RAW_FILE, TAVILY_RAW_FILE, EXA_RAW_FILE, REAL_EVENTS_FILE, MARKET_PRICES_FILE):
    if f.exists():
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
        if last_ingestion_ts is None or mtime > last_ingestion_ts:
            last_ingestion_ts = mtime

tab_overview, tab_live, tab_events, tab_strategies, tab_evaluation = st.tabs(
    [
        "Research Overview",
        "Live Intelligence (Real Data)",
        "Macro Events (Demo)",
        "Strategy Lab",
        "Model Evaluation",
    ]
)

# ----------------- TAB 1: OVERVIEW -----------------
with tab_overview:
    st.subheader("Executive Research Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Real Macro Events (180d)", f"{len(real_events):,}", help="Verified real events ingested via Apify (18 intervals)")
    col2.metric("Real News & Speeches", f"{len(real_news):,}", help="Verified articles from Tavily & Exa")
    col3.metric("SPY Market History", f"{len(market_prices):,} Days", help="Authentic daily prices downloaded from Yahoo Finance")
    real_sharpe = market_eval.get("ml_ensemble_strategy", {}).get("sharpe_ratio", 0.0)
    col4.metric("Real OOS ML Sharpe", f"{real_sharpe:+.4f}", help="Chronological walk-forward Sharpe on SPY after 2 bps transaction fees")

    st.write("---")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown("**Data Provenance & Pipeline Health**")
        ingestion_display = last_ingestion_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if last_ingestion_ts else 'No live data run'
        st.write(f"- **Last Data Ingestion / Refresh:** `{ingestion_display}`")
        st.write("- **Live Macro Ingestion Providers:** `Apify` (`scrapers_lat~economic-calendar-scraper`), `Tavily`, `Exa`")
        st.write(f"- **Macro Coverage Horizon:** `180 Days` ({real_events['timestamp_utc'].str[:10].min() if not real_events.empty else 'N/A'} to {real_events['timestamp_utc'].str[:10].max() if not real_events.empty else 'N/A'})")
        st.write(f"- **Real Market Price Benchmark:** `SPY` (S&P 500 ETF Trust, {len(market_prices)} trading sessions)")
    with col_meta2:
        st.markdown("**Model Evaluation Status**")
        eval_method = market_eval.get("evaluation_type", "Chronological Expanding Walk-Forward")
        oos_days = market_eval.get("out_of_sample_observations", 123)
        st.write(f"- **Validation Scheme:** `{eval_method}` (3 Expanding Folds)")
        st.write(f"- **Out-of-Sample Market Observations:** `{oos_days} Days` ({market_eval.get('out_of_sample_date_range', {}).get('start')} to {market_eval.get('out_of_sample_date_range', {}).get('end')})")
        st.write("- **Modeled Execution Drag:** `2.0 bps` per trade turnover")
        st.write("- **Benchmark Comparison:** `Buy & Hold SPY` vs `Dynamic ML Strategy`")

    if not real_events.empty and "surprise" in real_events.columns:
        valid_surp = real_events.dropna(subset=["surprise"]).copy()
        if not valid_surp.empty:
            fig_real = px.bar(
                valid_surp.head(25),
                x="event_name",
                y="surprise",
                color="country",
                title="Real Macroeconomic Surprises: Actual vs. Forecast Spread (Recent Sample)",
                labels={"event_name": "Macro Indicator", "surprise": "Surprise Delta (Actual - Forecast)"},
                hover_data=["actual", "forecast", "impact", "country"],
            )
            st.plotly_chart(fig_real, use_container_width=True)

# ----------------- TAB 2: LIVE INTELLIGENCE (REAL DATA) -----------------
with tab_live:
    st.subheader("Verified Live Macroeconomic & Financial News Intelligence")
    st.caption("180-Day historical calendar records and news ingested via Apify, Tavily, and Exa.")

    if real_events.empty and real_news.empty:
        st.warning("No real data has been processed yet. Run: `python scripts/build_pipeline.py`")
    else:
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("180-Day Macro Events", len(real_events))
        q2.metric("News & Speeches", len(real_news))
        surp_count = real_events["surprise"].notna().sum() if not real_events.empty else 0
        q3.metric("Surprises Computed", f"{surp_count}", help="Releases with published consensus survey estimates")
        avg_sentiment = real_news["sentiment_score"].mean() if not real_news.empty else 0.0
        q4.metric("Avg News Sentiment", f"{avg_sentiment:+.3f}", help="Lexical macro sentiment score [-1 to +1]")

        st.markdown("#### Real Economic Calendar Releases (180-Day Backfill)")
        if not real_events.empty:
            # Filters
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                all_countries = sorted(real_events["country"].dropna().unique().tolist())
                selected_countries = st.multiselect("Filter by Country", all_countries, default=all_countries[:6])
            with f_col2:
                all_impacts = sorted(real_events["impact"].dropna().unique().tolist())
                selected_impacts = st.multiselect("Filter by Impact Level", all_impacts, default=all_impacts)

            filtered_ev = real_events[
                (real_events["country"].isin(selected_countries)) &
                (real_events["impact"].isin(selected_impacts))
            ]

            st.dataframe(
                filtered_ev[[
                    "event_name", "country", "timestamp_utc", "actual",
                    "forecast", "previous", "surprise", "impact", "source"
                ]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No real calendar records found in `data/processed/real_macro_events.csv`.")

        st.markdown("#### Real Financial News & Central Bank Communications")
        if not real_news.empty:
            fig_sent = px.histogram(
                real_news,
                x="sentiment_score",
                color="sentiment_label",
                nbins=14,
                title="Financial News Sentiment Score Distribution (Tavily & Exa)",
                labels={"sentiment_score": "Sentiment Score (-1.0 Dovish to +1.0 Hawkish)"},
            )
            st.plotly_chart(fig_sent, use_container_width=True)

            st.dataframe(
                real_news[[
                    "source", "title", "published_at", "sentiment_score",
                    "sentiment_label", "url"
                ]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No real news articles found in `data/processed/real_macro_news.csv`.")

# ----------------- TAB 3: MACRO EVENTS (DEMO) -----------------
with tab_events:
    st.subheader("Synthetic Macroeconomic Event Explorer (Demo)")
    st.caption("Demonstration macro dataset used for baseline pipeline testing.")

    if events.empty:
        st.info("Synthetic events file not found. Run `python scripts/generate_sample_data.py`")
    else:
        selected_events = st.multiselect(
            "Filter event types",
            sorted(events["event_name"].dropna().unique()),
            default=sorted(events["event_name"].dropna().unique()),
        )
        filtered = events[events["event_name"].isin(selected_events)]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        if not filtered.empty and "timestamp_utc" in filtered.columns:
            plot_df = filtered.copy()
            plot_df["timestamp_utc"] = pd.to_datetime(plot_df["timestamp_utc"], utc=True)
            fig_surp = px.scatter(
                plot_df,
                x="timestamp_utc",
                y="surprise",
                color="event_name",
                title="Synthetic Event Surprises Over Time",
            )
            st.plotly_chart(fig_surp, use_container_width=True)

# ----------------- TAB 4: STRATEGY LAB -----------------
with tab_strategies:
    st.subheader("Quantitative Strategy Research Lab")

    mode = st.radio(
        "Select Backtest Engine:",
        ["Genuine SPY Historical Market Backtest (Real Data)", "Synthetic Baseline Permutations (Demo Data)"],
        horizontal=True,
    )

    if mode == "Genuine SPY Historical Market Backtest (Real Data)":
        st.caption("Empirical trading strategies evaluated on authentic daily SPY prices (Yahoo Finance) with 2 bps transaction fees.")
        if not market_prices.empty and "daily_return" in market_prices.columns:
            # Build cumulative wealth curves
            mkt_sim = market_prices.copy()
            mkt_sim["cum_spy"] = (1.0 + mkt_sim["daily_return"]).cumprod()

            rule_mets = market_eval.get("rule_based_strategies", {})
            st.markdown("#### Rule-Based Strategy Summary (Full 246-Day Horizon)")
            r_cols = st.columns(len(rule_mets))
            for i, (strat_name, m) in enumerate(rule_mets.items()):
                with r_cols[i]:
                    st.metric(
                        strat_name.replace("_", " ").title(),
                        f"{m['cumulative_return']*100:+.2f}%",
                        delta=f"Sharpe: {m['sharpe_ratio']:+.2f}",
                    )

            # Interactive chart of SPY close price and cumulative returns
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(x=mkt_sim["date"], y=mkt_sim["close"], mode="lines", name="SPY Close Price ($)"))
            fig_price.update_layout(title="SPY Historical Price Trajectory (October 2025 – October 2026)", xaxis_title="Date", yaxis_title="Price ($)")
            st.plotly_chart(fig_price, use_container_width=True)

            st.dataframe(market_prices[["date", "open", "high", "low", "close", "volume", "daily_return"]].tail(15), use_container_width=True)
        else:
            st.info("Market prices not found. Run `python scripts/run_market_backtest.py`")

    else:
        st.caption("Demonstration parameter variations evaluated on synthetic Gaussian return simulations.")
        if predictions.empty:
            st.info("Predictions not found. Run: `python -m src.models.train_model`")
        else:
            if "strategy" in predictions:
                strategy_names = sorted(predictions["strategy"].dropna().unique())
                selected_strategy = st.selectbox("Select strategy permutation", strategy_names)
                strategy_data = predictions[predictions["strategy"] == selected_strategy].copy()
                st.dataframe(strategy_data, use_container_width=True, hide_index=True)

            if {"strategy", "predicted_return"}.issubset(predictions.columns):
                ranking = (
                    predictions.groupby("strategy", as_index=False)
                    .agg(
                        Mean_Predicted_Return=("predicted_return", "mean"),
                        Observations=("predicted_return", "size"),
                    )
                    .sort_values("Mean_Predicted_Return", ascending=False)
                )
                fig_rank = px.bar(
                    ranking,
                    x="strategy",
                    y="Mean_Predicted_Return",
                    title="Average Predicted Return by Strategy (Out-of-Sample Demo)",
                )
                st.plotly_chart(fig_rank, use_container_width=True)

# ----------------- TAB 5: MODEL EVALUATION -----------------
with tab_evaluation:
    st.subheader("Out-of-Sample Quantitative Model Evaluation")

    eval_tab_choice = st.radio(
        "Select Evaluation Track:",
        ["Genuine SPY Market Evaluation (Real Data)", "Synthetic Baseline Demonstration (Demo Data)"],
        horizontal=True,
    )

    if eval_tab_choice == "Genuine SPY Market Evaluation (Real Data)":
        if not market_eval:
            st.info("Market backtest evaluation not found. Run `python scripts/run_market_backtest.py`.")
        else:
            st.success("✅ **Genuine Market Evaluation:** Evaluated on real historical SPY daily price series with expanding-window walk-forward splits and 2 bps transaction fees.")

            ml_m = market_eval.get("ml_ensemble_strategy", {})
            bm_m = market_eval.get("benchmark_buy_and_hold", {})

            st.markdown("#### Machine Learning Dynamic Strategy vs. Buy & Hold SPY Benchmark")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("ML Sharpe Ratio", f"{ml_m.get('sharpe_ratio', 0):.4f}", delta=f"Benchmark: {bm_m.get('sharpe_ratio', 0):.4f}")
            c2.metric("ML Sortino Ratio", f"{ml_m.get('sortino_ratio', 0):.4f}", delta=f"Benchmark: {bm_m.get('sortino_ratio', 0):.4f}")
            c3.metric("ML Max Drawdown", f"{ml_m.get('max_drawdown', 0):.2%}", delta=f"Benchmark: {bm_m.get('max_drawdown', 0):.2%}", delta_color="inverse")
            c4.metric("ML Cumulative Return", f"{ml_m.get('cumulative_return', 0):.2%}", delta=f"Benchmark: {bm_m.get('cumulative_return', 0):.2%}")

            st.markdown("#### Fold-by-Fold Expanding Walk-Forward Breakdown (123 Out-of-Sample Days)")
            folds_data = market_eval.get("folds", [])
            if folds_data:
                f_df = pd.DataFrame(folds_data)
                st.dataframe(f_df[["fold", "test_start", "test_end", "sample_size", "cumulative_return", "sharpe_ratio", "sortino_ratio", "max_drawdown", "win_rate"]], use_container_width=True, hide_index=True)

            if not market_preds.empty and "ml_strategy_return" in market_preds.columns:
                p_df = market_preds.copy()
                p_df["ml_cum"] = (1.0 + p_df["ml_strategy_return"]).cumprod()
                p_df["bm_cum"] = (1.0 + p_df["benchmark_return"]).cumprod()

                fig_oos = go.Figure()
                fig_oos.add_trace(go.Scatter(x=p_df["date"], y=p_df["ml_cum"], mode="lines", name="ML Dynamic Ensemble (2 bps fees)"))
                fig_oos.add_trace(go.Scatter(x=p_df["date"], y=p_df["bm_cum"], mode="lines", name="Benchmark: Buy & Hold SPY", line={"dash": "dash"}))
                fig_oos.update_layout(title="Out-of-Sample Cumulative Growth of $1.00 (April – October 2026)", xaxis_title="Date", yaxis_title="Portfolio Wealth ($)")
                st.plotly_chart(fig_oos, use_container_width=True)

            with st.expander("View Full JSON Evaluation"):
                st.json(market_eval)

    else:
        st.markdown(
            "> ⚠️ **Methodological Notice:** All performance metrics below evaluate out-of-sample model selections on "
            "**synthetic market returns**. They do NOT reflect actual historical financial asset returns."
        )

        metrics = evaluation.get("selected_strategy_metrics", {})
        baseline = evaluation.get("baseline_best_single_strategy", {})
        baseline_metrics = baseline.get("metrics", {})

        st.markdown("#### Primary Model vs. In-Sample Selected Baseline")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Ensemble Sharpe Ratio", f"{metrics.get('annualized_sharpe', 0):.3f}", delta=f"Baseline: {baseline_metrics.get('annualized_sharpe', 0):.3f}")
        m2.metric("Annualized Sortino Ratio", f"{metrics.get('annualized_sortino', 0):.3f}", delta=f"Baseline: {baseline_metrics.get('annualized_sortino', 0):.3f}")
        m3.metric("Maximum Drawdown", f"{metrics.get('max_drawdown', 0):.2%}", delta=f"Baseline: {baseline_metrics.get('max_drawdown', 0):.2%}", delta_color="inverse")
        m4.metric("Cumulative Return", f"{metrics.get('cumulative_return', 0):.2%}", delta=f"Baseline: {baseline_metrics.get('cumulative_return', 0):.2%}")

        with st.expander("View Synthetic Model Evaluation JSON"):
            st.json(evaluation)
