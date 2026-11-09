from pathlib import Path
from unittest.mock import patch

import pandas as pd
from pyquery import PyQuery as pq
import pytest
import requests

from sportsipy import utils
from sportsipy._basketball import parse_line_score
from sportsipy.nba.boxscore import Boxscore as NBABoxscore
from sportsipy.ncaab.boxscore import Boxscore as CollegeBoxscore


FIXTURES = Path(__file__).parents[1] / 'fixtures' / 'basketball'


def line_score(regulation, overtime=(), missing=None):
    periods = [str(i + 1) for i in range(regulation)] + list(overtime)
    cells = ''.join('<td data-stat="%s">%s</td>' % (
        label, '' if label == missing else 10) for label in periods)
    return pq('<table><tbody>' + ''.join(
        '<tr>%s<td data-stat="T">%s</td></tr>' % (
            cells, len(periods) * 10) for _ in range(2)) + '</tbody></table>')


@pytest.mark.parametrize('regulation', [2, 4])
@pytest.mark.parametrize('labels', [
    (), ('OT',), ('1OT',), ('OT1',), ('OT', '2OT'), ('OT1', 'OT2'),
    ('1OT', '2OT', '3OT')])
def test_period_variants(regulation, labels):
    summary, count = parse_line_score(line_score(regulation, labels),
                                      regulation)
    assert count == len(labels)
    assert summary == dict.fromkeys(('away', 'home'),
                                    [10] * (regulation + len(labels)))


@pytest.mark.parametrize('table', [
    pq('<div/>'), pq('<table/>'), line_score(2, ('2OT',)),
    line_score(2, ('OT',), missing='OT'), line_score(2, missing='1')])
def test_unknown_is_not_regulation(table):
    assert parse_line_score(table, 2)[1] is None


def test_mismatched_teams_are_unknown():
    table = line_score(2, ('OT',))
    table('tr:last td[data-stat="OT"]').remove()
    assert parse_line_score(table, 2)[1] is None


def test_inconsistent_totals_are_unknown():
    table = line_score(2)
    table('tr:last td[data-stat="T"]').text('100')
    assert parse_line_score(table, 2)[1] is None


@pytest.mark.parametrize('league,cls,uri,base,expected,summary', [
    ('nba', NBABoxscore, '202611070GSW', 'nba/202002220UTA.html', 1,
     {'away': [19, 22, 37, 32, 9], 'home': [31, 26, 20, 33, 16]}),
    ('ncaam', CollegeBoxscore, '2026-11-06-00-purdue',
     'ncaab/2020-01-22-19-louisville.html', 2,
     {'away': [20, 38, 12, 13], 'home': [32, 26, 12, 10]}),
])
def test_real_commented_line_score_in_boxscore_dataframe(
        league, cls, uri, base, expected, summary):
    # Keep the rest of each existing boxscore fixture intact so this exercises
    # the actual ingestion parser and dataframe export, without extra fetches.
    original = Path(__file__).parents[1] / 'integration' / 'boxscore' / base
    page = pq(utils._remove_html_comment_tags(pq(original.read_text())))
    page('table#line_score, table#line-score').remove()
    page('body').append((FIXTURES / (league + '-overtime.html')).read_text())
    html = str(page)
    with patch('sportsipy.utils._rate_limit_pq', return_value=pq(html)) as get:
        game = cls(uri)
    get.assert_called_once()
    assert game.overtimes == expected
    assert game.summary == summary
    assert game.dataframe.index.tolist() == [uri]
    assert game.dataframe.at[uri, 'overtimes'] == expected


@pytest.mark.parametrize('cls', [NBABoxscore, CollegeBoxscore])
def test_missing_boxscore_remains_empty(cls):
    with patch.object(cls, '_retrieve_html_page', return_value=None):
        game = cls('unplayed')
    assert game.overtimes is None
    assert game.dataframe is None


def test_unknown_overtime_exports_as_null():
    base = (Path(__file__).parents[1] /
            'integration/boxscore/nba/202002220UTA.html')
    page = pq(utils._remove_html_comment_tags(pq(base.read_text())))
    page('table#line_score').remove()
    with patch('sportsipy.utils._rate_limit_pq', return_value=page):
        game = NBABoxscore('unknown')
    assert game.overtimes is None
    assert pd.isna(game.dataframe.at['unknown', 'overtimes'])


@pytest.mark.parametrize('cls', [NBABoxscore, CollegeBoxscore])
@pytest.mark.parametrize('status', [404, 403, 429, 503])
def test_only_missing_boxscores_are_silently_empty(cls, status):
    response = requests.Response()
    response.status_code = status
    error = requests.HTTPError(response=response)
    with patch('sportsipy.utils._rate_limit_pq', side_effect=error):
        if status == 404:
            assert cls('missing').dataframe is None
        else:
            with pytest.raises(requests.HTTPError):
                cls('failed')


@pytest.mark.parametrize('prefix', ['', 'NBA In-Season Tournament\n'])
def test_nba_metadata_with_tournament_and_trailing_newline(prefix):
    lines = (prefix + '7:30 PM, November 9, 2018\n'
             'State Farm Arena, Atlanta, Georgia\n'
             'Logos via Sports Logos.net / About logos\n').splitlines()
    page = pq('<div class="scorebox_meta">' + ''.join(
        '<div>%s</div>' % line for line in lines) + '</div>')
    game = NBABoxscore.__new__(NBABoxscore)
    assert game._parse_game_date_and_location('date', page) == (
        '7:30 PM, November 9, 2018')
    assert game._parse_game_date_and_location('location', page) == (
        'State Farm Arena, Atlanta, Georgia')
