from datetime import date

import pytest

from src.ingestion import clients


class Response:
    status_code = 200
    ok = True

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class Session:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response(self.data)


def test_apify_chunking_and_header(monkeypatch):
    monkeypatch.setenv('APIFY_API_TOKEN', 'SECRET')
    monkeypatch.setenv('APIFY_ACTOR_ID', 'owner~actor')
    session = Session([{'eventName': 'CPI'}])
    result = clients.apify_events(date(2026, 1, 1), date(2026, 3, 1), session=session)
    assert len(session.calls) == 2
    assert len(result) == 2
    assert 'SECRET' not in session.calls[0][0]
    assert session.calls[0][1]['headers']['Authorization'] == 'Bearer SECRET'
    assert session.calls[0][1]['json']['dateFrom'] == '2026-01-01'


def test_tavily_normalization(monkeypatch):
    monkeypatch.setenv('TAVILY_API_KEY', 'SECRET')
    session = Session({'results': [{'title': 'CPI report', 'url': 'https://example.org', 'content': 'inflation'}]})
    assert clients.tavily_news('CPI', session=session)[0]['source'] == 'tavily'
    assert 'SECRET' not in session.calls[0][0]


def test_exa_normalization(monkeypatch):
    monkeypatch.setenv('EXA_API_KEY', 'SECRET')
    session = Session({
        'results': [
            {'title': 'FOMC', 'publishedDate': '2026-10-01', 'url': 'https://example.com/fomc', 'text': 'Meeting statement'},
        ]
    })
    records = clients.exa_news('FOMC', session=session)
    assert records[0]['title'] == 'FOMC'
    assert records[0]['text'] == 'Meeting statement'
    assert records[0]['source'] == 'exa'
    assert records[0]['url'] == 'https://example.com/fomc'
    assert records[0]['published_at'] == '2026-10-01'
    assert session.calls[0][1]['headers']['x-api-key'] == 'SECRET'
    assert session.calls[0][1]['json']['contents'] == {'text': True}
    assert 'SECRET' not in session.calls[0][0]


def test_exa_summary_and_missing_content(monkeypatch):
    monkeypatch.setenv('EXA_API_KEY', 'SECRET')
    session = Session({
        'results': [
            {'title': 'CPI', 'publishedDate': '2026-10-02', 'summary': 'Inflation summary'},
            {'title': 'GDP', 'publishedDate': '2026-10-03', 'text': '   ', 'summary': None},
            {'title': 'NFP', 'publishedDate': '2026-10-04'},
        ]
    })
    records = clients.exa_news('macro', session=session)
    assert records[0]['text'] == 'Inflation summary'
    assert records[1]['text'] is None
    assert records[1]['title'] == 'GDP'
    assert records[2]['text'] is None
    assert records[2]['title'] == 'NFP'


def test_missing_key(monkeypatch):
    monkeypatch.delenv('TAVILY_API_KEY', raising=False)
    with pytest.raises(clients.IngestionError, match='TAVILY_API_KEY'):
        clients.tavily_news('CPI', session=Session({}))


def test_event_normalization_keeps_missing_values():
    row = clients.normalize_macro_events([{'eventName': 'CPI', 'actualValue': 3.1}])[0]
    assert row['actual'] == 3.1
    assert row['forecast'] is None
    assert row['previous'] is None
    assert row['surprise'] is None


def test_clean_numeric_html_entities_and_invalid_values():
    assert clients.clean_numeric('&nbsp;') is None
    assert clients.clean_numeric('&#160;') is None
    assert clients.clean_numeric('  &nbsp;  ') is None
    assert clients.clean_numeric('') is None
    assert clients.clean_numeric('   ') is None
    assert clients.clean_numeric('N/A') is None
    assert clients.clean_numeric('-') is None
    assert clients.clean_numeric('--') is None
    assert clients.clean_numeric(None) is None
    assert clients.clean_numeric('  51.3% ') == 51.3
    assert clients.clean_numeric('1,250.5') == 1250.5
    assert clients.clean_numeric(-1) == -1.0
    assert clients.clean_numeric('3.2') == 3.2


def test_normalize_macro_events_previous_and_surprise():
    raw = [{
        'eventName': 'Core CPI',
        'eventDate': '2026-10-10',
        'timeGmt': '12:30',
        'country': 'United States',
        'actualValue': '3.2%',
        'forecastValue': '3.0%',
        'previousValue': '3.1%',
        'impact': 'High',
    }]
    row = clients.normalize_macro_events(raw)[0]
    assert row['event_name'] == 'Core CPI'
    assert row['actual'] == 3.2
    assert row['forecast'] == 3.0
    assert row['previous'] == 3.1
    assert row['surprise'] == 0.2
    assert row['country'] == 'United States'
    assert row['impact'] == 'High'
    assert row['timestamp_utc'] == '2026-10-10T12:30:00+00:00'
    assert row['timezone_original'] == 'GMT'


def test_timestamp_utc_handling_without_silent_guessing():
    # Explicit GMT time -> normalized to UTC
    raw_gmt = [{'eventName': 'CPI', 'eventDate': '2026-10-05', 'timeGmt': '06:00'}]
    row_gmt = clients.normalize_macro_events(raw_gmt)[0]
    assert row_gmt['timestamp_utc'] == '2026-10-05T06:00:00+00:00'
    assert row_gmt['timezone_original'] == 'GMT'

    # Missing timezone -> does NOT guess UTC silently
    raw_unknown = [{'eventName': 'Retail Sales', 'eventDate': '2026-10-05', 'time': '06:00'}]
    row_unknown = clients.normalize_macro_events(raw_unknown)[0]
    assert row_unknown['timestamp_utc'] is None
    assert row_unknown['timezone_original'] == 'unspecified'


def test_deduplication_of_macro_events():
    duplicate_events = [
        {'eventName': 'PMI', 'eventDate': '2026-10-05', 'timeGmt': '18:00', 'country': 'Australia'},
        {'eventName': 'PMI', 'eventDate': '2026-10-05', 'timeGmt': '18:00', 'country': 'Australia'},
        {'eventName': 'GDP', 'eventDate': '2026-10-06', 'timeGmt': '10:00', 'country': 'Japan'},
    ]
    rows = clients.normalize_macro_events(duplicate_events)
    assert len(rows) == 2
    assert [r['event_name'] for r in rows] == ['PMI', 'GDP']


def test_url_deduplication_in_tavily_and_exa(monkeypatch):
    monkeypatch.setenv('TAVILY_API_KEY', 'SECRET')
    monkeypatch.setenv('EXA_API_KEY', 'SECRET')

    tavily_session = Session({
        'results': [
            {'title': 'Article 1', 'url': 'https://news.com/article1', 'content': 'Text 1'},
            {'title': 'Article 1 Duplicate', 'url': 'https://news.com/article1', 'content': 'Text 1 dup'},
            {'title': 'Article 2', 'url': 'https://news.com/article2', 'content': 'Text 2'},
        ]
    })
    t_records = clients.tavily_news('query', session=tavily_session)
    assert len(t_records) == 2
    assert [r['url'] for r in t_records] == ['https://news.com/article1', 'https://news.com/article2']

    exa_session = Session({
        'results': [
            {'title': 'Exa 1', 'url': 'https://exa.com/doc1', 'text': 'Content 1'},
            {'title': 'Exa 1 Dup', 'url': 'https://exa.com/doc1', 'text': 'Content 1 dup'},
            {'title': 'Exa 2', 'url': 'https://exa.com/doc2', 'text': 'Content 2'},
        ]
    })
    e_records = clients.exa_news('query', session=exa_session)
    assert len(e_records) == 2
    assert [r['url'] for r in e_records] == ['https://exa.com/doc1', 'https://exa.com/doc2']


def test_lexical_sentiment_analysis():
    from src.ingestion.pipeline import analyze_lexical_sentiment
    score_pos, label_pos = analyze_lexical_sentiment("FOMC rate hike to contain inflation with robust expansion and payroll gains")
    assert score_pos > 0
    assert label_pos == "hawkish/positive"

    score_neg, label_neg = analyze_lexical_sentiment("Recession risks, growth slowdown, and trade tariffs threaten economic slump")
    assert score_neg < 0
    assert label_neg == "dovish/negative"

    score_neutral, label_neutral = analyze_lexical_sentiment("Economic calendar meeting scheduled for Tuesday")
    assert score_neutral == 0.0
    assert label_neutral == "neutral"


def test_real_pipeline_processing():
    from src.ingestion.pipeline import (
        load_and_process_real_events,
        load_and_process_real_news,
    )
    events_df = load_and_process_real_events()
    news_df = load_and_process_real_news()

    assert not events_df.empty
    assert "data_provenance" in events_df.columns
    assert (events_df["data_provenance"] == "real_verified").all()
    assert "event_id" in events_df.columns
    assert events_df["event_id"].is_unique

    assert not news_df.empty
    assert "sentiment_score" in news_df.columns
    assert "data_provenance" in news_df.columns
