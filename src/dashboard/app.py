import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
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
    "🛡️ **System Status & Data Separation:** "
    "Macroeconomic indicators and central bank news in the **Live Intelligence** tab reflect **verified real-world API data**. "
    "Market price returns and Strategy Lab evaluations use **synthetic Monte Carlo simulations** for illustrative research purposes."
)

# Safe data loaders
events = pd.read_csv(EVENTS_FILE) if EVENTS_FILE.exists() else pd.DataFrame()
features = pd.read_csv(FEATURES_FILE) if FEATURES_FILE.exists() else pd.DataFrame()
predictions = pd.read_csv(PREDICTIONS_FILE) if PREDICTIONS_FILE.exists() else pd.DataFrame()

real_events = pd.read_csv(REAL_EVENTS_FILE) if REAL_EVENTS_FILE.exists() else pd.DataFrame()
real_news = pd.read_csv(REAL_NEWS_FILE) if REAL_NEWS_FILE.exists() else pd.DataFrame()

evaluation = {}
if EVALUATION_FILE.exists():
    try:
        with open(EVALUATION_FILE) as file:
            evaluation = json.load(file)
    except (json.JSONDecodeError, OSError):
        evaluation = {}

# Compute last ingestion time
last_ingestion_ts = None
for f in (APIFY_RAW_FILE, TAVILY_RAW_FILE, EXA_RAW_FILE, REAL_EVENTS_FILE):
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
    col1.metric("Real Macro Events", f"{len(real_events):,}", help="Verified real events ingested via Apify")
    col2.metric("Real News Articles", f"{len(real_news):,}", help="Verified articles from Tavily & Exa")
    col3.metric("Demo Research Events", f"{len(events):,}", help="Synthetic macro events for strategy testing")
    col4.metric("OOS Strategy Forecasts", f"{len(predictions):,}", help="Out-of-sample walk-forward predictions")

    st.write("---")

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown("**Data Provenance & Pipeline Health**")
        ingestion_display = last_ingestion_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if last_ingestion_ts else 'No live data run'
        st.write(f"- **Last Live Ingestion:** `{ingestion_display}`")
        st.write("- **Configured Ingestion Providers:** `Apify`, `Tavily`, `Exa`")
        st.write(f"- **Feature Engineering Status:** `{'Ready' if not features.empty else 'Not Built'}` (Leakage-Safe Expanding Windows)")
    with col_meta2:
        st.markdown("**Model Evaluation Status**")
        eval_method = evaluation.get('evaluation', 'Expanding Walk-Forward')
        data_status = evaluation.get('data_status', 'synthetic_demo')
        st.write(f"- **Validation Architecture:** `{eval_method}`")
        st.write(f"- **Strategy Target Source:** `{data_status}`")
        st.write(f"- **Walk-Forward Folds Completed:** `{evaluation.get('folds_completed', 0)}`")

    if not real_events.empty and "surprise" in real_events.columns:
        valid_surp = real_events.dropna(subset=["surprise"]).copy()
        if not valid_surp.empty:
            fig_real = px.bar(
                valid_surp,
                x="event_name",
                y="surprise",
                color="country",
                title="Real Macroeconomic Indicator Surprises (Actual vs. Forecast)",
                labels={"event_name": "Event Indicator", "surprise": "Actual - Forecast Surprise"},
                hover_data=["actual", "forecast", "impact", "country"],
            )
            st.plotly_chart(fig_real, use_container_width=True)

# ----------------- TAB 2: LIVE INTELLIGENCE (REAL DATA) -----------------
with tab_live:
    st.subheader("Verified Live Macroeconomic & Financial News Intelligence")
    st.caption("Live external data ingested via Apify Economic Calendar, Tavily Search, and Exa Neural Search.")

    if real_events.empty and real_news.empty:
        st.warning("No real data has been processed yet. Run: `python scripts/build_pipeline.py`")
    else:
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Live Calendar Records", len(real_events))
        q2.metric("Live News Headlines", len(real_news))
        missing_actuals = real_events["actual"].isna().sum() if not real_events.empty else 0
        missing_forecasts = real_events["forecast"].isna().sum() if not real_events.empty else 0
        q3.metric("Missing Forecasts", f"{missing_forecasts}", help="Events published without consensus estimates")
        avg_sentiment = real_news["sentiment_score"].mean() if not real_news.empty else 0.0
        q4.metric("Avg News Sentiment", f"{avg_sentiment:+.3f}", help="Lexical macro sentiment score [-1 to +1]")

        st.markdown("#### Real Economic Calendar Releases")
        if not real_events.empty:
            st.dataframe(
                real_events[[
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
            # Sentiment breakdown chart
            fig_sent = px.histogram(
                real_news,
                x="sentiment_score",
                color="sentiment_label",
                nbins=12,
                title="Financial News Sentiment Score Distribution",
                labels={"sentiment_score": "Sentiment Score (-1.0 Dovish/Neg to +1.0 Hawkish/Pos)"},
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
    st.caption("Demonstration macro dataset used for strategy feature engineering.")

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
    st.subheader("Walk-Forward Strategy Research Lab")
    st.caption("Out-of-sample evaluations across momentum and mean-reversion strategies.")

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
                title="Average Predicted Return by Strategy (Out-of-Sample)",
            )
            st.plotly_chart(fig_rank, use_container_width=True)

# ----------------- TAB 5: MODEL EVALUATION -----------------
with tab_evaluation:
    st.subheader("Out-of-Sample Quantitative Model Evaluation")

    if not evaluation:
        st.info("Evaluation report not found. Run `python -m src.models.train_model` first.")
    else:
        st.markdown(
            "> ⚠️ **Methodological Notice:** All performance metrics below evaluate out-of-sample model selections on "
            "**synthetic market returns**. They do NOT reflect actual historical financial asset returns or live trade execution."
        )

        metrics = evaluation.get("selected_strategy_metrics", {})
        baseline = evaluation.get("baseline_best_single_strategy", {})
        baseline_metrics = baseline.get("metrics", {})

        st.markdown("#### Primary Model vs. In-Sample Selected Baseline")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Ensemble Sharpe Ratio",
            f"{metrics.get('annualized_sharpe', 0):.3f}",
            delta=f"Baseline: {baseline_metrics.get('annualized_sharpe', 0):.3f}",
        )
        m2.metric(
            "Annualized Sortino Ratio",
            f"{metrics.get('annualized_sortino', 0):.3f}",
            delta=f"Baseline: {baseline_metrics.get('annualized_sortino', 0):.3f}",
        )
        m3.metric(
            "Maximum Drawdown",
            f"{metrics.get('max_drawdown', 0):.2%}",
            delta=f"Baseline: {baseline_metrics.get('max_drawdown', 0):.2%}",
            delta_color="inverse",
        )
        m4.metric(
            "Cumulative Return",
            f"{metrics.get('cumulative_return', 0):.2%}",
            delta=f"Baseline: {baseline_metrics.get('cumulative_return', 0):.2%}",
        )

        st.markdown("#### Complete Model Evaluation Schema")
        st.json(evaluation)
