import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.nhl.constants import SEASON_PAGE_URL
from sportsreference.nhl.teams import Teams


MONTH = 1
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('NHL_%s_all_stats.html' % YEAR)

    html_contents = read_file('NHL_%s.html' % YEAR)
    return MockPQ(html_contents)


def mock_request(url):
    class MockRequest:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if str(YEAR) in url:
        return MockRequest('good')
    else:
        return MockRequest('bad', status_code=404)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNHLIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
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

    def test_nhl_integration_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['DET'])

        detroit = self.teams('DET')
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, detroit.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nhl_integration_all_teams_dataframe_returns_dataframe(self):
        result = self.teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.abbreviations)
        assert set(result.columns.values) == set(self.results.keys())

    def test_nhl_invalid_team_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.teams('INVALID_NAME')

    def test_nhl_empty_page_returns_no_teams(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0


class TestNHLIntegrationInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)

        teams = Teams()

        for team in teams:
            assert team._year == '2017'
