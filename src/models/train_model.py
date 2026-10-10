
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "strategy_dataset.csv"
REPORTS = ROOT / "reports"
MODELS = ROOT / "data" / "processed"

NUMERIC = [
    "daily_surprise",
    "event_count",
    "lagged_surprise",
    "historical_volatility",
    "day_of_week",
    "month",
    "lookback",
    "threshold",
]

CATEGORICAL = ["strategy"]
TARGET = "target_return"


def make_model() -> Pipeline:
    """Build a reproducible regression pipeline."""
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC),
            (
                "strategy",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=200,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def performance_metrics(returns: pd.Series) -> dict:
    """Calculate illustrative annualized risk and return metrics."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]

    if len(values) == 0:
        raise ValueError("Cannot evaluate an empty return series")

    volatility = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    downside = np.minimum(values, 0.0)
    downside_deviation = float(np.sqrt(np.mean(downside ** 2)))

    sharpe = (
        float(np.mean(values) / volatility * np.sqrt(252))
        if volatility > 0 else 0.0
    )
    sortino = (
        float(np.mean(values) / downside_deviation * np.sqrt(252))
        if downside_deviation > 0 else 0.0
    )

    equity = np.cumprod(1.0 + values)
    peaks = np.maximum.accumulate(np.concatenate(([1.0], equity)))[1:]
    drawdowns = equity / peaks - 1.0
    max_drawdown = float(np.min(drawdowns))

    return {
        "observations": len(values),
        "mean_daily_return": float(np.mean(values)),
        "annualized_sharpe": sharpe,
        "annualized_sortino": sortino,
        "max_drawdown": max_drawdown,
        "cumulative_return": float(equity[-1] - 1.0),
    }


def walk_forward_evaluate(
    df: pd.DataFrame,
    folds: int = 3,
) -> tuple[pd.DataFrame, dict]:
    """Evaluate using expanding chronological training windows."""
    if folds < 1:
        raise ValueError("folds must be at least 1")

    required = set(NUMERIC + CATEGORICAL + [TARGET, "date"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"], utc=True, errors="raise")
    data = data.sort_values("date").reset_index(drop=True)

    if data[NUMERIC + [TARGET]].isna().any().any():
        raise ValueError("Features and target must not contain missing values")

    unique_dates = np.array(sorted(data["date"].unique()))
    if len(unique_dates) < (folds + 2) * 3:
        raise ValueError("Not enough dates for walk-forward evaluation")

    predictions = []
    n_dates = len(unique_dates)

    # Reserve the first half for initial training, then test on
    # consecutive unseen date blocks using expanding training windows.
    initial_train = n_dates // 2
    test_size = max(1, (n_dates - initial_train) // folds)

    for fold in range(folds):
        train_end = initial_train + fold * test_size
        test_end = min(train_end + test_size, n_dates)

        if train_end >= n_dates or train_end >= test_end:
            break

        train_dates = unique_dates[:train_end]
        test_dates = unique_dates[train_end:test_end]

        train = data[data["date"].isin(train_dates)]
        test = data[data["date"].isin(test_dates)].copy()

        model = make_model()
        model.fit(train[NUMERIC + CATEGORICAL], train[TARGET])

        test["predicted_return"] = model.predict(
            test[NUMERIC + CATEGORICAL]
        )
        test["fold"] = fold + 1
        predictions.append(test)

    if not predictions:
        raise ValueError("No walk-forward predictions were produced")

    result = pd.concat(predictions, ignore_index=True)

    # Choose one strategy per date based only on predictions.
    chosen = (
        result.sort_values("predicted_return")
        .groupby("date", as_index=False)
        .tail(1)
        .sort_values("date")
    )

    report = {
        "evaluation": "expanding_window_walk_forward",
        "data_status": "synthetic_demo_not_real_market_evidence",
        "market_return_source": "synthetic_random_normal_simulation",
        "disclaimer": "Market returns and strategy PnL are synthetic Monte Carlo demonstrations, not real market evidence or trade executions.",
        "folds_completed": int(result["fold"].nunique()),
        "training_observations_available": len(data),
        "out_of_sample_strategy_rows": len(result),
        "out_of_sample_dates": int(chosen["date"].nunique()),
        "selected_strategy_metrics": performance_metrics(
            chosen[TARGET]
        ),
        "baseline_best_single_strategy": {},
    }

    # A simple baseline selected on the initial training period only.
    first_test_date = result["date"].min()
    initial = data[data["date"] < first_test_date]

    if not initial.empty:
        baseline_name = (
            initial.groupby("strategy")[TARGET]
            .mean()
            .idxmax()
        )
        baseline_returns = (
            result[result["strategy"] == baseline_name]
            .sort_values("date")
            .drop_duplicates("date")[TARGET]
        )

        if not baseline_returns.empty:
            report["baseline_best_single_strategy"] = {
                "strategy": str(baseline_name),
                "metrics": performance_metrics(baseline_returns),
            }

    return result, report


def main() -> None:
    if not DATA.exists():
        raise FileNotFoundError(
            f"{DATA} not found. Build the strategy dataset first."
        )

    data = pd.read_csv(DATA)
    predictions, report = walk_forward_evaluate(data, folds=3)

    REPORTS.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)

    predictions.to_csv(
        REPORTS / "walk_forward_predictions.csv", index=False
    )

    with open(REPORTS / "model_evaluation.json", "w") as file:
        json.dump(report, file, indent=2, default=str)

    # Fit a final research model on all available data for reuse.
    final_model = make_model()
    final_model.fit(data[NUMERIC + CATEGORICAL], data[TARGET])
    joblib.dump(final_model, MODELS / "macro_strategy_model.joblib")

    print("SUCCESS: Walk-forward evaluation completed")
    print(f"Saved predictions: {REPORTS / 'walk_forward_predictions.csv'}")
    print(f"Saved evaluation: {REPORTS / 'model_evaluation.json'}")
    print(f"Saved model: {MODELS / 'macro_strategy_model.joblib'}")
    print("\nOut-of-sample selected-strategy metrics:")
    print(json.dumps(report["selected_strategy_metrics"], indent=2))
    print("\nIMPORTANT: Metrics use synthetic demonstration data.")


if __name__ == "__main__":
    main()
