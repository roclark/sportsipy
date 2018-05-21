import mock
import os
from flexmock import flexmock
from sportsreference import utils
from sportsreference.nfl.constants import SEASON_PAGE_URL
from sportsreference.nfl.teams import Teams


MONTH = 9
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl_stats', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'div#all_team_stats':
                return read_file('%s_all_team_stats.html' % YEAR)
            elif div == 'table#AFC':
                return read_file('%s_afc.html' % YEAR)
            else:
                return read_file('%s_nfc.html' % YEAR)

    html_contents = read_file('%s.html' % YEAR)
    return MockPQ(html_contents)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNFLIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'rank': 6,
            'abbreviation': 'KAN',
            'name': 'Kansas City Chiefs',
            'wins': 10,
            'losses': 6,
            'win_percentage': .625,
            'games_played': 16,
            'points_for': 415,
            'points_against': 339,
            'points_difference': 76,
            'margin_of_victory': 4.8,
            'strength_of_schedule': -1.3,
            'simple_rating_system': 3.4,
            'offensive_simple_rating_system': 3.8,
            'defensive_simple_rating_system': -0.3,
            'yards': 6007,
            'plays': 985,
            'yards_per_play': 6.1,
            'turnovers': 11,
            'fumbles': 3,
            'first_downs': 322,
            'pass_completions': 363,
            'pass_attempts': 543,
            'pass_yards': 4104,
            'pass_touchdowns': 26,
            'interceptions': 8,
            'pass_net_yards_per_attempt': 7.1,
            'pass_first_downs': 198,
            'rush_attempts': 405,
            'rush_yards': 1903,
            'rush_touchdowns': 12,
            'rush_yards_per_attempt': 4.7,
            'rush_first_downs': 95,
            'penalties': 118,
            'yards_from_penalties': 1044,
            'first_downs_from_penalties': 29,
            'percent_drives_with_points': 44.9,
            'percent_drives_with_turnovers': 6.3,
            'points_contributed_by_offense': 115.88
        }
        self.abbreviations = [
            'RAM', 'NWE', 'PHI', 'NOR', 'JAX', 'KAN', 'DET', 'PIT', 'RAV',
            'MIN', 'SEA', 'CAR', 'SDG', 'DAL', 'ATL', 'WAS', 'HTX', 'TAM',
            'OTI', 'SFO', 'GNB', 'BUF', 'RAI', 'NYJ', 'CRD', 'CIN', 'DEN',
            'MIA', 'CHI', 'CLT', 'NYG', 'CLE'
        ]
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.teams = Teams()

    def test_nfl_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_nfl_integration_returns_correct_attributes_for_team(self):
        kansas = self.teams('KAN')

        for attribute, value in self.results.items():
            assert getattr(kansas, attribute) == value

    def test_nfl_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations
