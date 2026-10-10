
import numpy as np
import pandas as pd
import pytest

from scripts.generate_sample_data import generate_macro_events


def test_data_is_not_empty():
    assert not generate_macro_events().empty


def test_event_ids_are_unique():
    assert generate_macro_events()["event_id"].is_unique


def test_surprise_is_correct():
    df = generate_macro_events()
    assert np.allclose(
        df["surprise"],
        df["actual"] - df["forecast"],
        atol=1e-12,
    )


def test_timestamps_are_valid():
    df = generate_macro_events()
    timestamps = pd.to_datetime(
        df["timestamp_utc"], utc=True
    )
    assert timestamps.notna().all()


def test_invalid_days_are_rejected():
    with pytest.raises(ValueError):
        generate_macro_events(days=0)
