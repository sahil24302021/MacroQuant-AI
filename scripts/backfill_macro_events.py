"""Backfill 180 days of real macroeconomic calendar events via Apify.

Queries the configured Apify actor across 180-day intervals,
deduplicates results, normalizes numeric values and surprises,
and outputs data/raw/apify_live.json and data/processed/real_macro_events.csv.
"""
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import os
from urllib.parse import quote

import pandas as pd

from src.ingestion.clients import (
    IngestionError,
    _key,
    _post,
    normalize_macro_events,
)


def run_backfill(days: int = 180, step_days: int = 11):
    end = date(2026, 10, 11)
    start = end - timedelta(days=days - 1)
    print(f"Executing Apify backfill from {start} to {end} ({days} days)...")

    actor = os.getenv("APIFY_ACTOR_ID", "").strip()
    if not actor:
        raise RuntimeError("APIFY_ACTOR_ID is not configured in .env")
    url = f"https://api.apify.com/v2/acts/{quote(actor, safe='~')}/run-sync-get-dataset-items"
    headers = {
        "Authorization": f"Bearer {_key('APIFY_API_TOKEN')}",
        "Content-Type": "application/json",
    }

    # Generate sampling dates across the 180-day window
    sample_dates = []
    curr = start
    while curr <= end:
        sample_dates.append(curr)
        curr += timedelta(days=step_days)
    if end not in sample_dates:
        sample_dates.append(end)

    print(f"Generated {len(sample_dates)} sampling intervals across {days} days.")

    all_raw_items = []
    for idx, d in enumerate(sample_dates):
        chunk_end = min(d + timedelta(days=step_days - 1), end)
        payload = {
            "dateFrom": d.isoformat(),
            "dateTo": chunk_end.isoformat(),
            "aiEventImpact": False,
        }
        print(f"[{idx+1}/{len(sample_dates)}] Fetching {d.isoformat()} to {chunk_end.isoformat()}...")
        try:
            items = _post(url, headers, payload, timeout=120)
            if isinstance(items, list):
                print(f"   -> Retrieved {len(items)} items")
                all_raw_items.extend(items)
            else:
                print(f"   -> Unexpected response shape: {type(items)}")
        except (IngestionError, ValueError, RuntimeError) as e:
            print(f"   -> Warning on interval {d}: {e}")
        time.sleep(0.5)

    print(f"\nTotal raw items collected: {len(all_raw_items)}")

    # Deduplicate raw items
    raw_dedup = []
    seen_raw = set()
    for it in all_raw_items:
        key = (
            it.get("eventDate"),
            it.get("eventName"),
            it.get("country"),
            str(it.get("actualValue")),
            str(it.get("forecastValue")),
        )
        if key not in seen_raw:
            seen_raw.add(key)
            raw_dedup.append(it)

    print(f"Unique raw items after deduplication: {len(raw_dedup)}")

    # Save raw payload to data/raw/apify_live.json (ignored by git)
    raw_dest = ROOT / "data" / "raw" / "apify_live.json"
    raw_dest.parent.mkdir(parents=True, exist_ok=True)
    raw_dest.write_text(json.dumps(raw_dedup, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(raw_dedup)} raw items to {raw_dest.relative_to(ROOT)}")

    # Normalize records
    normalized = normalize_macro_events(raw_dedup)
    df = pd.DataFrame(normalized)
    # Sort chronologically
    if "event_date" in df.columns:
        df["event_date"] = pd.to_datetime(df["event_date"])
        df = df.sort_values(by=["event_date", "event_name"]).reset_index(drop=True)
        df["event_date"] = df["event_date"].dt.strftime("%Y-%m-%d")

    proc_dest = ROOT / "data" / "processed" / "real_macro_events.csv"
    proc_dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(proc_dest, index=False)
    print(f"Saved {len(df)} normalized records to {proc_dest.relative_to(ROOT)}")

    # Coverage summary
    earliest = df["event_date"].min() if not df.empty else None
    latest = df["event_date"].max() if not df.empty else None
    unique_events = df["event_name"].nunique() if not df.empty else 0
    countries = df["country"].nunique() if not df.empty else 0
    with_forecast = df["forecast"].notna().sum() if not df.empty else 0
    with_actual = df["actual"].notna().sum() if not df.empty else 0
    with_surprise = df["surprise"].notna().sum() if not df.empty else 0

    print("\n--- COVERAGE SUMMARY ---")
    print(f"Earliest event date: {earliest}")
    print(f"Latest event date:   {latest}")
    print(f"Total events:        {len(df)}")
    print(f"Unique event names:  {unique_events}")
    print(f"Unique countries:    {countries}")
    print(f"With actual:         {with_actual}")
    print(f"With forecast:       {with_forecast}")
    print(f"With surprise delta: {with_surprise}")

    return df


if __name__ == "__main__":
    run_backfill()
