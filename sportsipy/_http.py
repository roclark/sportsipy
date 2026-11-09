"""Shared, rate-limited HTML transport for Sports Reference pages."""

from collections import OrderedDict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import os
from pathlib import Path
import tempfile
import threading
import time

import cloudscraper
from filelock import FileLock
import requests


_local = threading.local()
_cache = OrderedDict()
_cache_lock = threading.RLock()
_RETRY_STATUSES = {429, 500, 502, 503, 504}


def _session():
    # Sessions and cookies belong to one thread and process.
    if getattr(_local, 'pid', None) != os.getpid():
        _local.session = cloudscraper.create_scraper()
        _local.pid = os.getpid()
    return _local.session


def _retry_after(response):
    value = response.headers.get('Retry-After', '')
    try:
        return max(0, float(value))
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            return max(0, (date - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return 0


def _download(url, interval=10):
    """Perform one attempt, sharing a cooldown across local processes."""
    directory = Path(os.environ.get(
        'SPORTSIPY_RATE_LIMIT_DIR',
        str(Path(tempfile.gettempdir()) / 'sportsipy-rate-limit')))
    directory.mkdir(parents=True, exist_ok=True)
    state = directory / 'next-request'
    interval = max(10.0, float(interval), float(os.environ.get(
        'SPORTSIPY_REQUEST_INTERVAL', '10')))
    timeout = float(os.environ.get('SPORTSIPY_REQUEST_TIMEOUT', '30'))
    # Hold the lock through the request. A crash releases the OS lock; the
    # pre-written cooldown prevents an immediate burst after a killed worker.
    with FileLock(str(directory / 'requests.lock')):
        try:
            remaining = float(state.read_text()) - time.time()
        except (FileNotFoundError, ValueError):
            remaining = 0
        if remaining > 0:
            time.sleep(remaining)
        cooldown = interval
        _write_cooldown(state, interval)
        try:
            response = _session().get(url, timeout=timeout)
            if response.status_code in _RETRY_STATUSES:
                cooldown = max(interval, _retry_after(response))
            return response
        finally:
            _write_cooldown(state, cooldown)


def _write_cooldown(state, seconds):
    temporary = state.with_suffix('.tmp')
    temporary.write_text(str(time.time() + seconds))
    temporary.replace(state)


def fetch_html(url, interval=10):
    """Fetch HTML, retry transient failures, and briefly reuse successes."""
    ttl = max(0, float(os.environ.get('SPORTSIPY_CACHE_TTL', '60')))
    with _cache_lock:
        cached = _cache.get(url)
        if cached and time.monotonic() - cached[0] < ttl:
            _cache.move_to_end(url)
            return cached[1]
    retries = max(0, int(os.environ.get('SPORTSIPY_REQUEST_RETRIES', '2')))
    for attempt in range(retries + 1):
        try:
            response = _download(url, interval=interval)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == retries:
                raise
            continue
        if response.status_code in _RETRY_STATUSES and attempt < retries:
            continue
        response.raise_for_status()
        html = response.text
        # Challenge pages occasionally arrive with HTTP 200. Never cache or
        # parse those as empty seasons or completed games.
        lowered = html.lower()
        if any(marker in lowered for marker in (
                '<title>just a moment', '<title>access denied',
                '<title>verify you are human')):
            raise requests.HTTPError('Received a challenge page',
                                     response=response)
        with _cache_lock:
            _cache[url] = (time.monotonic(), html)
            _cache.move_to_end(url)
            while len(_cache) > 128:
                _cache.popitem(last=False)
        return html
