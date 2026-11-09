from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
import multiprocessing
from types import SimpleNamespace
import time
from unittest.mock import Mock

import pytest
import requests

from sportsipy import _http, utils


_download = _http._download


def response(status=200, html='<html>game</html>', headers=None):
    result = requests.Response()
    result.status_code = status
    result._content = html.encode()
    result.headers.update(headers or {})
    return result


class Clock:
    def __init__(self):
        self.now = 1000
        self.sleeps = []

    def time(self):
        return self.now

    monotonic = time

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def test_session_reuse_and_process_ownership(monkeypatch):
    monkeypatch.setattr(_http, '_local', SimpleNamespace())
    factory = Mock(side_effect=[object(), object()])
    monkeypatch.setattr(_http.cloudscraper, 'create_scraper', factory)
    first = _http._session()
    assert _http._session() is first
    monkeypatch.setattr(_http.os, 'getpid', lambda: -1)
    assert _http._session() is not first
    assert factory.call_count == 2


def test_shared_cooldown_and_retry_after(monkeypatch):
    clock = Clock()
    get = Mock(side_effect=[response(429, headers={'Retry-After': '45'}),
                            response()])
    monkeypatch.setattr(_http, 'time', clock)
    monkeypatch.setattr(_http, '_session', lambda: SimpleNamespace(get=get))
    _download('https://example.test/first')
    _download('https://example.test/second')
    assert clock.sleeps == [45]
    assert get.call_args.kwargs == {'timeout': 30}


def test_failed_request_keeps_cooldown(monkeypatch):
    clock = Clock()
    get = Mock(side_effect=[requests.Timeout(), response()])
    monkeypatch.setattr(_http, 'time', clock)
    monkeypatch.setattr(_http, '_session', lambda: SimpleNamespace(get=get))
    with pytest.raises(requests.Timeout):
        _download('https://example.test/first')
    _download('https://example.test/second', interval=0)
    assert clock.sleeps == [10]


def test_retry_after_http_date():
    date = format_datetime(datetime.now(timezone.utc) + timedelta(seconds=60))
    delay = _http._retry_after(response(headers={'Retry-After': date}))
    assert 58 <= delay <= 60
    invalid = response(headers={'Retry-After': 'invalid'})
    assert _http._retry_after(invalid) == 0


def test_retry_and_reuse_valid_html(monkeypatch):
    download = Mock(side_effect=[response(429), response(503), response()])
    monkeypatch.setattr(_http, '_download', download)
    assert _http.fetch_html('url') == '<html>game</html>'
    assert _http.fetch_html('url') == '<html>game</html>'
    assert download.call_count == 3


@pytest.mark.parametrize('failure', [
    response(403), response(404), response(429), response(503)])
def test_failures_are_not_cached(monkeypatch, failure):
    download = Mock(return_value=failure)
    monkeypatch.setattr(_http, '_download', download)
    for _ in range(2):
        with pytest.raises(requests.HTTPError):
            _http.fetch_html('url')
    expected = 6 if failure.status_code in (429, 503) else 2
    assert download.call_count == expected
    assert not _http._cache


def test_challenge_is_not_cached(monkeypatch):
    monkeypatch.setattr(_http, '_download', Mock(return_value=response(
        html='<html><title>Just a moment...</title></html>')))
    with pytest.raises(requests.HTTPError):
        _http.fetch_html('url')
    assert not _http._cache


def test_bounded_timeout_retries(monkeypatch):
    download = Mock(side_effect=requests.Timeout)
    monkeypatch.setattr(_http, '_download', download)
    with pytest.raises(requests.Timeout):
        _http.fetch_html('url')
    assert download.call_count == 3


def test_cache_expiry_disable_and_fresh_parse(monkeypatch):
    clock = Clock()
    download = Mock(return_value=response())
    monkeypatch.setattr(_http, 'time', clock)
    monkeypatch.setattr(_http, '_download', download)
    first = utils._rate_limit_pq('url')
    first('html').remove()
    assert utils._rate_limit_pq('url')('html')
    assert download.call_count == 1
    clock.now += 61
    utils._rate_limit_pq('url')
    assert download.call_count == 2
    monkeypatch.setenv('SPORTSIPY_CACHE_TTL', '0')
    utils._rate_limit_pq('url')
    utils._rate_limit_pq('url')
    assert download.call_count == 4


def test_url_check_reuses_get_and_does_not_hide_rate_limit(monkeypatch):
    download = Mock(return_value=response())
    monkeypatch.setattr(_http, '_download', download)
    assert utils._url_exists('url')
    utils._rate_limit_pq('url')
    assert download.call_count == 1
    download.return_value = response(429)
    with pytest.raises(requests.HTTPError):
        utils._url_exists('other')


def _process_download(directory, queue):
    import os
    os.environ['SPORTSIPY_RATE_LIMIT_DIR'] = directory
    os.environ['SPORTSIPY_REQUEST_INTERVAL'] = '10'

    def get(url, **kwargs):
        queue.put(time.monotonic())
        return response()

    _http._session = lambda: SimpleNamespace(get=get)
    _http._download('https://example.test/no-network')


def test_cooldown_coordinates_separate_processes(tmp_path):
    context = multiprocessing.get_context('spawn')
    queue = context.Queue()
    processes = [
        context.Process(target=_process_download, args=(str(tmp_path), queue))
        for _ in range(2)]
    try:
        for process in processes:
            process.start()
        starts = sorted(queue.get(timeout=30) for _ in processes)
        assert starts[1] - starts[0] >= 9.9
        for process in processes:
            process.join(timeout=10)
            assert process.exitcode == 0
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join()
        queue.close()
