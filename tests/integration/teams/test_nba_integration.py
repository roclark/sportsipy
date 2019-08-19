import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.nba.constants import SEASON_PAGE_URL
from sportsreference.nba.teams import Teams


MONTH = 1
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


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


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'div#all_team-stats-base':
                return read_file('%s_team.html' % YEAR)
            else:
                return read_file('%s_opponent.html' % YEAR)

    html_contents = read_file('NBA_%s.html' % YEAR)
    return MockPQ(html_contents)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNBAIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'rank': 26,
            'abbreviation': 'DET',
            'name': 'Detroit Pistons',
            'games_played': 82,
            'minutes_played': 19805,
            'field_goals': 3269,
            'field_goal_attempts': 7282,
            'field_goal_percentage': .449,
            'three_point_field_goals': 631,
            'three_point_field_goal_attempts': 1915,
            'three_point_field_goal_percentage': .330,
            'two_point_field_goals': 2638,
            'two_point_field_goal_attempts': 5367,
            'two_point_field_goal_percentage': .492,
            'free_throws': 1140,
            'free_throw_attempts': 1586,
            'free_throw_percentage': .719,
            'offensive_rebounds': 908,
            'defensive_rebounds': 2838,
            'total_rebounds': 3746,
            'assists': 1732,
            'steals': 574,
            'blocks': 310,
            'turnovers': 973,
            'personal_fouls': 1467,
            'points': 8309,
            'opp_field_goals': 3144,
            'opp_field_goal_attempts': 6830,
            'opp_field_goal_percentage': .460,
            'opp_three_point_field_goals': 767,
            'opp_three_point_field_goal_attempts': 2098,
            'opp_three_point_field_goal_percentage': .366,
            'opp_two_point_field_goals': 2377,
            'opp_two_point_field_goal_attempts': 4732,
            'opp_two_point_field_goal_percentage': .502,
            'opp_free_throws': 1346,
            'opp_free_throw_attempts': 1726,
            'opp_free_throw_percentage': .780,
            'opp_offensive_rebounds': 656,
            'opp_defensive_rebounds': 2861,
            'opp_total_rebounds': 3517,
            'opp_assists': 1929,
            'opp_steals': 551,
            'opp_blocks': 339,
            'opp_turnovers': 1046,
            'opp_personal_fouls': 1434,
            'opp_points': 8401
        }
        self.abbreviations = [
            'BOS', 'CLE', 'TOR', 'WAS', 'ATL', 'MIL', 'IND', 'CHI', 'MIA',
            'DET', 'CHO', 'NYK', 'ORL', 'PHI', 'BRK', 'GSW', 'SAS', 'HOU',
            'LAC', 'UTA', 'OKC', 'MEM', 'POR', 'DEN', 'NOP', 'DAL', 'SAC',
            'MIN', 'LAL', 'PHO'
        ]
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.teams = Teams()

    def test_nba_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_nba_integration_returns_correct_attributes_for_team(self):
        detroit = self.teams('DET')

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_nba_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations

    def test_nba_integration_dataframe_returns_dataframe(self):
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

    def test_nba_integration_all_teams_dataframe_returns_dataframe(self):
        result = self.teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.abbreviations)
        assert set(result.columns.values) == set(self.results.keys())

    def test_nba_invalid_team_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.teams('INVALID_NAME')

    def test_nba_empty_page_returns_no_teams(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0


class TestNBAIntegrationInvalidDate:
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
