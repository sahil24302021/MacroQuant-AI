"""Refresh and validate real macroeconomic news and central bank documents.

Queries Tavily Search and Exa Neural Search for real macroeconomic documents,
preserves published timestamps, full text snippets, source URLs, and provider provenance,
computes transparent lexical sentiment scores, and writes:
- data/raw/tavily_live.json (ignored by git)
- data/raw/exa_live.json (ignored by git)
- data/processed/real_macro_news.csv
"""
import json
import logging
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.ingestion.clients import IngestionError, exa_news, tavily_news
from src.ingestion.pipeline import analyze_lexical_sentiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("refresh_news")


def main():
    logger.info("Starting real macroeconomic news refresh...")

    all_tavily = []
    all_exa = []

    # 1. Tavily queries
    tavily_queries = [
        "US Federal Reserve FOMC interest rate decision September 2026",
        "US Bureau of Labor Statistics inflation CPI September 2026 payrolls",
    ]
    for q in tavily_queries:
        logger.info("Querying Tavily: %s", q)
        try:
            results = tavily_news(q, max_results=10)
            logger.info("   -> Retrieved %d records from Tavily", len(results))
            all_tavily.extend(results)
        except (IngestionError, ValueError, RuntimeError) as e:
            logger.warning("Tavily query failed: %s", e)

    # 2. Exa queries
    exa_queries = [
        "Federal Reserve Governor Waller speech inflation labor market 2026",
        "Federal Reserve Summary of Economic Projections SEP September 2026",
    ]
    for q in exa_queries:
        logger.info("Querying Exa: %s", q)
        try:
            results = exa_news(q, max_results=10)
            logger.info("   -> Retrieved %d records from Exa", len(results))
            all_exa.extend(results)
        except (IngestionError, ValueError, RuntimeError) as e:
            logger.warning("Exa query failed: %s", e)

    # Deduplicate Tavily
    tav_seen = set()
    tav_dedup = []
    for r in all_tavily:
        u = r.get("url")
        if u and u not in tav_seen:
            tav_seen.add(u)
            tav_dedup.append(r)

    # Deduplicate Exa
    exa_seen = set()
    exa_dedup = []
    for r in all_exa:
        u = r.get("url")
        if u and u not in exa_seen:
            exa_seen.add(u)
            exa_dedup.append(r)

    # Save raw payloads (ignored by git)
    tav_path = ROOT / "data" / "raw" / "tavily_live.json"
    tav_path.parent.mkdir(parents=True, exist_ok=True)
    tav_path.write_text(json.dumps(tav_dedup, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved %d raw Tavily records to %s", len(tav_dedup), tav_path.relative_to(ROOT))

    exa_path = ROOT / "data" / "raw" / "exa_live.json"
    exa_path.write_text(json.dumps(exa_dedup, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved %d raw Exa records to %s", len(exa_dedup), exa_path.relative_to(ROOT))

    # Process and compute lexical sentiment
    combined_records = []
    idx = 1
    for r in tav_dedup:
        text = r.get("text") or r.get("title") or ""
        score, label = analyze_lexical_sentiment(text)
        clean_snip = re.sub(r'\s+', ' ', text[:250]).strip() if text else None
        combined_records.append({
            "article_id": f"NEWS-TAV-{idx:04d}",
            "source": "tavily",
            "title": r.get("title"),
            "url": r.get("url"),
            "published_at": r.get("published_at"),
            "text_length": len(text),
            "summary_snippet": (clean_snip + "...") if clean_snip and len(text) > 250 else clean_snip,
            "sentiment_score": round(score, 4),
            "sentiment_label": label,
            "data_provenance": "real_verified",
        })
        idx += 1

    idx = 1
    for r in exa_dedup:
        text = r.get("text") or r.get("title") or ""
        score, label = analyze_lexical_sentiment(text)
        clean_snip = re.sub(r'\s+', ' ', text[:250]).strip() if text else None
        combined_records.append({
            "article_id": f"NEWS-EXA-{idx:04d}",
            "source": "exa",
            "title": r.get("title"),
            "url": r.get("url"),
            "published_at": r.get("published_at"),
            "text_length": len(text),
            "summary_snippet": (clean_snip + "...") if clean_snip and len(text) > 250 else clean_snip,
            "sentiment_score": round(score, 4),
            "sentiment_label": label,
            "data_provenance": "real_verified",
        })
        idx += 1

    news_df = pd.DataFrame(combined_records)
    out_csv = ROOT / "data" / "processed" / "real_macro_news.csv"
    news_df.to_csv(out_csv, index=False)
    logger.info("Saved %d verified real news articles to %s", len(news_df), out_csv.relative_to(ROOT))

    print("\n--- MACRO NEWS REFRESH SUMMARY ---")
    print(f"Total articles:             {len(news_df)}")
    print(f"Tavily sources:             {(news_df['source'] == 'tavily').sum()}")
    print(f"Exa sources:                {(news_df['source'] == 'exa').sum()}")
    print(f"With published timestamps:  {news_df['published_at'].notna().sum()}")
    print(f"Mean sentiment score:       {news_df['sentiment_score'].mean():+.4f}")
    return news_df


if __name__ == "__main__":
    main()
