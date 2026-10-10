"""Execute the MacroQuant AI data pipeline.

Loads ingested live data (Apify, Tavily, Exa), validates and cleans records,
produces processed CSV datasets, and generates the macro outlook report.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingestion.pipeline import run_pipeline


def main():
    print("=" * 60)
    print("MacroQuant AI — Real Data Processing Pipeline")
    print("=" * 60)

    results = run_pipeline()

    print(f"Processed Real Macro Events: {results['events_count']}")
    if results['events_csv']:
        print(f"Saved Events CSV: {results['events_csv']}")

    print(f"Processed Real Macro News:   {results['news_count']}")
    if results['news_csv']:
        print(f"Saved News CSV:   {results['news_csv']}")

    print(f"Generated Macro Outlook:     {results['outlook_path']}")
    print("=" * 60)
    print("SUCCESS: Pipeline completed with verified real data.")


if __name__ == "__main__":
    main()
