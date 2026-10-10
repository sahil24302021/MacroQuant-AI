"""API ingestion clients. Credentials never enter URLs or exception messages."""
import html
import math
import os
import re
import time
from datetime import UTC, date, datetime, timedelta
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()


class IngestionError(RuntimeError):
    pass


def _key(name: str) -> str:
    value = os.getenv(name, '').strip()
    if not value:
        raise IngestionError(f'{name} is not configured')
    return value


def _post(url: str, headers: dict, payload: dict, session=None, timeout: int = 60):
    client = session or requests.Session()
    for attempt in range(3):
        try:
            response = client.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(0.5 * (2 ** attempt))
                continue
            if not response.ok:
                raise IngestionError(f'API request failed (HTTP {response.status_code})')
            return response.json()
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 2:
                raise IngestionError('API connection failed after retries') from None
            time.sleep(0.5 * (2 ** attempt))
        except ValueError:
            raise IngestionError('API returned invalid JSON') from None
    raise IngestionError('API request failed')


def clean_numeric(val):
    """Clean HTML entities and parse finite float, returning None for missing/invalid data."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if math.isfinite(val) else None
    if not isinstance(val, str):
        return None

    cleaned = html.unescape(val)
    cleaned = cleaned.replace('\xa0', ' ').replace('&nbsp;', ' ')
    cleaned = re.sub(r'<[^>]+>', '', cleaned).strip()

    if not cleaned or cleaned.lower() in ('n/a', '-', '--', 'null', 'none', 'nan'):
        return None

    cleaned = cleaned.replace('%', '').replace(',', '').strip()
    try:
        num = float(cleaned)
        return num if math.isfinite(num) else None
    except (ValueError, TypeError):
        return None


def parse_utc_timestamp(event_date: str | None, event_time: str | None, raw_item: dict | None = None) -> str | None:
    """Parse event timestamp to ISO-8601 UTC string if timezone is explicit or GMT."""
    raw_item = raw_item or {}
    for key in ('timestamp_utc', 'timestampUtc', 'timestamp', 'datetime'):
        raw_ts = raw_item.get(key)
        if isinstance(raw_ts, str) and raw_ts.strip():
            try:
                dt = datetime.fromisoformat(raw_ts)
                if dt.tzinfo is not None:
                    return dt.astimezone(UTC).isoformat()
            except (ValueError, TypeError):
                pass

    if not event_date or not isinstance(event_date, str):
        return None
    if not event_time or not isinstance(event_time, str):
        return None

    date_str = event_date.strip()
    time_str = event_time.strip()

    is_gmt = bool(raw_item.get('timeGmt')) or 'gmt' in time_str.lower() or 'utc' in time_str.lower()
    clean_time = time_str.lower().replace('gmt', '').replace('utc', '').strip()

    parts = clean_time.split(':')
    if len(parts) == 2:
        clean_time = f"{int(parts[0]):02d}:{int(parts[1]):02d}:00"
    elif len(parts) == 3:
        clean_time = f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
    else:
        return None

    if is_gmt:
        try:
            dt = datetime.fromisoformat(f"{date_str}T{clean_time}+00:00")
            return dt.isoformat()
        except (ValueError, TypeError):
            return None

    return None


def apify_events(start: date, end: date, *, session=None, actor_input: dict | None = None, country: str | None = None, impact: str | None = None):
    """Run configured actor in <=30-day inclusive chunks; actor-specific fields overridable."""
    if end < start:
        raise ValueError('end must not precede start')
    actor = os.getenv('APIFY_ACTOR_ID', '').strip()
    if not actor:
        raise IngestionError('APIFY_ACTOR_ID is not configured')
    headers = {'Authorization': f'Bearer {_key("APIFY_API_TOKEN")}', 'Content-Type': 'application/json'}
    url = f'https://api.apify.com/v2/acts/{quote(actor, safe="~")}/run-sync-get-dataset-items'
    items = []
    cursor = start

    base_input = dict(actor_input or {})
    if country and 'country' not in base_input:
        base_input['country'] = country
    if impact and 'impact' not in base_input:
        base_input['impact'] = impact

    while cursor <= end:
        last = min(cursor + timedelta(days=29), end)
        payload = {**base_input, 'dateFrom': cursor.isoformat(), 'dateTo': last.isoformat()}
        data = _post(url, headers, payload, session=session, timeout=310)
        if not isinstance(data, list):
            raise IngestionError('Apify returned unexpected dataset shape')
        items.extend(data)
        cursor = last + timedelta(days=1)
    return items


def tavily_news(query: str, *, session=None, max_results: int = 10):
    data = _post('https://api.tavily.com/search',
                 {'Authorization': f'Bearer {_key("TAVILY_API_KEY")}', 'Content-Type': 'application/json'},
                 {'query': query, 'max_results': max_results, 'search_depth': 'basic'}, session=session)
    if not isinstance(data, dict) or not isinstance(data.get('results'), list):
        raise IngestionError('Tavily returned unexpected results shape')
    records = []
    seen_urls = set()
    for r in data['results']:
        if not isinstance(r, dict):
            continue
        url = r.get('url')
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        records.append({
            'source': 'tavily',
            'title': r.get('title'),
            'url': url,
            'published_at': r.get('published_date'),
            'text': (r.get('content') or '').strip() or None,
        })
    return records


def _extract_text(result: dict) -> str | None:
    for key in ('text', 'summary'):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def exa_news(query: str, *, session=None, max_results: int = 10, contents: dict | None = None):
    payload = {
        'query': query,
        'type': 'auto',
        'numResults': max_results,
        'contents': contents or {'text': True},
    }
    data = _post('https://api.exa.ai/search',
                 {'x-api-key': _key('EXA_API_KEY'), 'Content-Type': 'application/json'},
                 payload, session=session)
    if not isinstance(data, dict) or not isinstance(data.get('results'), list):
        raise IngestionError('Exa returned unexpected results shape')
    records = []
    seen_urls = set()
    for r in data['results']:
        if not isinstance(r, dict):
            continue
        url = r.get('url')
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        records.append({
            'source': 'exa',
            'title': r.get('title'),
            'url': url,
            'published_at': r.get('publishedDate'),
            'text': _extract_text(r),
        })
    return records


def normalize_macro_events(items: list) -> list:
    """Preserve raw event values, clean HTML/entities, and avoid duplicate events."""
    normalized = []
    seen = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        name = (item.get('eventName') or item.get('event_name') or item.get('name') or item.get('event') or '').strip() or None
        ev_date = (item.get('eventDate') or item.get('event_date') or item.get('date') or '').strip() or None
        ev_time = (item.get('timeGmt') or item.get('event_time') or item.get('time') or '').strip() or None
        country = (item.get('country') or '').strip() or None

        actual = clean_numeric(item.get('actualValue') if item.get('actualValue') is not None else item.get('actual'))
        forecast = clean_numeric(item.get('forecastValue') if item.get('forecastValue') is not None else item.get('forecast'))
        previous = clean_numeric(item.get('previousValue') if item.get('previousValue') is not None else item.get('previous'))

        if name is not None and ev_date is not None:
            dedup_key = (name, ev_date, ev_time, country, actual, forecast)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

        surprise = round(actual - forecast, 6) if (actual is not None and forecast is not None) else None
        ts_utc = parse_utc_timestamp(ev_date, ev_time, item)
        orig_tz = 'GMT' if (item.get('timeGmt') or 'gmt' in str(item.get('time', '')).lower()) else (item.get('timezone') or 'unspecified')

        normalized.append({
            'source': 'apify',
            'event_name': name,
            'event_date': ev_date,
            'event_time': ev_time,
            'timestamp_utc': ts_utc,
            'timezone_original': orig_tz,
            'country': country,
            'actual': actual,
            'forecast': forecast,
            'previous': previous,
            'surprise': surprise,
            'impact': (item.get('impact') or item.get('importance') or '').strip() or None,
        })
    return normalized
