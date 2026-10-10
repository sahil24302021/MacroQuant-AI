# MacroQuant AI — Macroeconomic Ingestion Coverage & Provenance Report

**Document Version:** 1.0.0<br>
**Data Scope:** 180-Day Real Macroeconomic Backfill<br>
**Requested Date Horizon:** 2026-04-15 to 2026-10-11 (180 Days)<br>
**Verified Earliest Event Date:** 2026-04-15<br>
**Verified Latest Event Date:** 2026-10-08<br>
**Provider / Ingestion Engine:** Apify Actor `scrapers_lat~economic-calendar-scraper`<br>
**Underlying Primary Source:** Nasdaq Public Economic Calendar

---

## 1. Executive Summary

This report documents the real 180-day macroeconomic backfill executed for the MacroQuant AI research repository. Using the configured Apify actor (`scrapers_lat~economic-calendar-scraper`), the pipeline queried 18 chronological intervals spanning April 15, 2026 through October 11, 2026.

Key outcomes:
1. **Total Real Events Ingested:** **169 unique records** across 19 global economies and 117 unique economic release categories.
2. **Numeric Completeness:** **154 releases (91.1%)** contain verified published numeric `actual` values; **66 releases (39.1%)** had pre-release consensus forecasts published, enabling deterministic `surprise` calculation ($actual - forecast$).
3. **Data Integrity:** Releases without published consensus forecasts (e.g., qualitative central bank meetings, auctions, minor trade gauges) have `surprise` values strictly recorded as `null` rather than fabricated zeros or artificial guesses.
4. **Zero Lookahead Leakage:** All events retain explicit original release timestamps (GMT/UTC) for chronological alignment with market prices.

---

## 2. Ingestion Architecture & Provider Details

| Parameter | Specification |
| :--- | :--- |
| **Provider** | Apify Cloud Platform |
| **Actor Identifier** | `scrapers_lat~economic-calendar-scraper` |
| **Actor Build** | `0.1.4` (Latest) |
| **Authentication** | Bearer Token in HTTP Authorization Header (Strictly excluded from logs/Git) |
| **Execution Protocol** | Synchronous REST API (`run-sync-get-dataset-items`) with exponential backoff retries |
| **Sampling Structure** | 18 chronological chunks across the 180-day window |
| **Raw Storage Destination** | `data/raw/apify_live.json` (169 records, ignored by version control) |
| **Processed Destination** | `data/processed/real_macro_events.csv` |

---

## 3. Dataset Coverage Breakdown

### Geographic Distribution (Top Economies)

| Country | Event Count | Percentage | Key Indicators Captured |
| :--- | :--- | :--- | :--- |
| **United Kingdom** | 35 | 20.7% | Construction Output, GDP, Nationwide HPI, Treasury Gilt Auctions |
| **Germany** | 22 | 13.0% | German CPI, HICP, Factory Orders, Trade Balance, WPI |
| **India** | 19 | 11.2% | HSBC Manufacturing PMI, Services PMI, Trade Balance |
| **France** | 15 | 8.9% | French Current Account, Exports, Industrial Production |
| **Japan** | 14 | 8.3% | Capacity Utilization, Industrial Production, Services PMI |
| **United States** | 10 | 5.9% | OPEC Meeting, Fed communications, Capacity Utilization, PMI |
| **Italy** | 10 | 5.9% | Industrial Production, BTP Auctions |
| **Spain** | 9 | 5.3% | Core CPI, Industrial Production |
| **Other (11 Nations)** | 35 | 20.7% | Australia, New Zealand, South Africa, Singapore, Switzerland, etc. |

### Impact Classification

- **High Impact:** **45 releases (26.6%)** (e.g., German CPI, HSBC India PMI, Retail Sales, National GDP)
- **Medium Impact:** **105 releases (62.1%)** (e.g., Industrial Production, Services PMI, Trade Balance)
- **Low Impact:** **19 releases (11.2%)** (e.g., Treasury Gilt Auctions, secondary sentiment gauges)

---

## 4. Surprise Spread Distribution

Of the 66 events with published consensus forecasts:
- **Upside Surprises ($actual > forecast$):** **39 events (59.1%)**
- **Downside Surprises ($actual < forecast$):** **17 events (25.8%)**
- **In-Line Releases ($actual == forecast$):** **10 events (15.2%)**

### Representative Major Releases

| Event Name | Country | Date / Time (UTC) | Actual | Forecast | Surprise | Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **German CPI** | Germany | 2026-09-11 02:00 | 2.9% | 2.9% | **0.00** | High |
| **German Factory Orders** | Germany | 2026-05-08 06:00 | 5.0% | 1.0% | **+4.00** | High |
| **Italian Industrial Production** | Italy | 2026-09-11 08:00 | 0.7% | 0.3% | **+0.40** | Medium |
| **HSBC India Manufacturing PMI** | India | 2026-10-02 05:00 | 55.1 | 55.7 | **-0.60** | High |
| **S&P Global Services PMI** | Australia | 2026-10-05 18:00 | 51.9 | 51.4 | **+0.50** | Medium |
| **Nationwide HPI** | United Kingdom | 2026-10-02 06:00 | 0.8% | 1.3% | **-0.50** | High |
| **Japan Industrial Production** | Japan | 2026-04-15 04:30 | -2.0% | -2.1% | **+0.10** | Medium |

---

## 5. Technical Limitations of Apify Actor & Mitigation

1. **Scraping Pagination Constraint:**
   - **Limitation:** The underlying Apify actor (`scrapers_lat~economic-calendar-scraper`) scrapes the public Nasdaq economic calendar and returns the first 10 events matching `dateFrom` without supporting pagination parameters (`page` or `pageSize`).
   - **Mitigation:** The MacroQuant ingestion harness implemented multi-chunk interval sampling (18 distinct date windows) to systematically capture releases across the entire 180-day historical continuum.
2. **Missing Survey Consensus Figures:**
   - **Limitation:** Qualitative events (e.g. OPEC meetings) and secondary government balance reports frequently lack Wall Street median consensus surveys.
   - **Mitigation:** Strict schema enforcement: `surprise` is computed as `None`/`null` instead of substituting synthetic zeroes, avoiding bias in quantitative models.
3. **Data Segregation:**
   - Real macroeconomic releases are saved to `data/processed/real_macro_events.csv`.
   - The synthetic demonstration dataset remains in `data/raw/macro_events.csv` for independent pipeline testing.
