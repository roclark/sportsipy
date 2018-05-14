import os
from flexmock import flexmock
from mocker import Mocker, MockerTestCase
from pyquery import PyQuery
from sportsreference import utils
from sportsreference.nhl.constants import SEASON_PAGE_URL
from sportsreference.nhl.teams import Teams


MONTH = 1
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl_stats', filename)
    return open('%s' % filepath, 'r').read()


class MockPQ:
    def __init__(self, html_contents):
        self.html_contents = html_contents

    def __call__(self, div):
        return read_file('NHL_%s_all_stats.html' % YEAR)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNHLIntegration(MockerTestCase):
    def setUp(self):
        self.results = {
            'rank': 25,
            'abbreviation': 'DET',
            'name': 'Detroit Red Wings',
            'average_age': 28.4,
            'games_played': 82,
            'wins': 33,
            'losses': 36,
            'overtime_losses': 13,
            'points': 79,
            'points_percentage': .482,
            'goals_for': 207,
            'goals_against': 244,
            'simple_rating_system': -0.41,
            'strength_of_schedule': 0.04,
            'total_goals_per_game': 5.50,
            'power_play_goals': 38,
            'power_play_opportunities': 252,
            'power_play_percentage': 15.08,
            'power_play_goals_against': 45,
            'power_play_opportunities_against': 235,
            'penalty_killing_percentage': 80.85,
            'short_handed_goals': 3,
            'short_handed_goals_against': 9,
            'shots_on_goal': 2335,
            'shooting_percentage': 8.5,
            'shots_against': 2507,
            'save_percentage': .903,
            'pdo_at_even_strength': 99.6
        }
        self.abbreviations = [
            'WSH', 'PIT', 'CHI', 'CBJ', 'MIN', 'ANA', 'MTL', 'EDM', 'NYR',
            'STL', 'SJS', 'OTT', 'TOR', 'BOS', 'TBL', 'NYI', 'NSH', 'CGY',
            'PHI', 'WPG', 'CAR', 'LAK', 'FLA', 'DAL', 'DET', 'BUF', 'ARI',
            'NJD', 'VAN', 'COL'
        ]
        html_contents = read_file('NHL_%s.html' % YEAR)

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        mock_pyquery = self.mocker.replace(PyQuery)
        mock_pyquery(SEASON_PAGE_URL % YEAR)
        self.mocker.result(MockPQ(html_contents))
        self.mocker.replay()

        self.teams = Teams()

    def test_nhl_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_nhl_integration_returns_correct_attributes_for_team(self):
        detroit = self.teams('DET')

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_nhl_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations
