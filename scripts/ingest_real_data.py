"""Run with --live to use billable external services. Dry-run is the default."""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingestion.clients import (
    IngestionError,
    apify_events,
    exa_news,
    normalize_macro_events,
    tavily_news,
)


def main():
    parser = argparse.ArgumentParser(description="Ingest macroeconomic events and financial news from live APIs.")
    parser.add_argument('--live', action='store_true', help='Make real API requests (may incur charges)')
    parser.add_argument('--provider', choices=['apify', 'tavily', 'exa'], required=True, help='API data provider')
    parser.add_argument('--days', type=int, default=180, help='Lookback period in days (1-180)')
    parser.add_argument('--country', type=str, default=None, help='Filter by country name for Apify (e.g., "United States")')
    parser.add_argument('--impact', type=str, default=None, help='Filter by event impact for Apify (e.g., "High")')
    parser.add_argument('--output', type=str, default=None, help='Custom JSON destination path')
    args = parser.parse_args()

    if not 1 <= args.days <= 180:
        parser.error('--days must be between 1 and 180')

    if not args.live:
        print(f'DRY RUN: {args.provider}, {args.days} days. No API request made.')
        return

    try:
        if args.provider == 'apify':
            end = date.today()
            raw_items = apify_events(
                end - timedelta(days=args.days - 1),
                end,
                country=args.country,
                impact=args.impact,
            )
            result = normalize_macro_events(raw_items)
        elif args.provider == 'tavily':
            result = tavily_news('US inflation CPI Federal Reserve FOMC jobs report economic outlook')
        else:
            result = exa_news('US inflation CPI Federal Reserve FOMC jobs report economic outlook')
    except IngestionError as error:
        parser.exit(1, f'Ingestion error: {error}\n')

    dest_path = Path(args.output) if args.output else ROOT / 'data' / 'raw' / f'{args.provider}_live.json'
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    rel_path = dest_path.relative_to(ROOT) if dest_path.is_relative_to(ROOT) else dest_path
    print(f'Saved {len(result)} records to {rel_path}')


if __name__ == '__main__':
    main()
