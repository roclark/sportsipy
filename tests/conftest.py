"""Keep the regression suite offline and transport caches isolated."""

import socket
import sys

import pytest

from sportsipy import _http


@pytest.fixture(autouse=True)
def offline_transport(monkeypatch, tmp_path):
    def blocked(*args, **kwargs):
        raise AssertionError('Tests must use saved HTML, not the network')

    monkeypatch.setattr(socket, 'getaddrinfo', blocked)
    monkeypatch.setattr(_http, '_download', blocked)
    monkeypatch.setenv('SPORTSIPY_RATE_LIMIT_DIR', str(tmp_path / 'rate'))
    _http._cache.clear()
    # Old unit tests install PropertyMock descriptors directly on classes.
    # Restore them so those tests cannot change later fixture-based results.
    classes = {}
    for name, module in list(sys.modules.items()):
        if name.startswith(('sportsipy.nba.', 'sportsipy.ncaab.')):
            for value in vars(module).values():
                if isinstance(value, type) and value.__module__ == name:
                    classes[value] = dict(vars(value))
    yield
    _http._cache.clear()
    for cls, before in classes.items():
        after = dict(vars(cls))
        for name in after.keys() - before.keys():
            delattr(cls, name)
        for name, value in before.items():
            if name not in ('__dict__', '__weakref__'):
                if after.get(name) is not value:
                    setattr(cls, name, value)
