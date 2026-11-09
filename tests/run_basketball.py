"""Run this fork's maintained suite consistently across shells and OSes."""

from pathlib import Path
import sys

import pytest


def main():
    root = Path(__file__).parent
    files = {root / 'unit' / name for name in (
        'test_utils.py', 'test_basketball_overtimes.py',
        'test_http_transport.py')}
    for league in ('nba', 'ncaab'):
        files.update(root.rglob('test_%s*.py' % league))
    return pytest.main([str(path) for path in sorted(files)] + sys.argv[1:])


if __name__ == '__main__':
    sys.exit(main())
