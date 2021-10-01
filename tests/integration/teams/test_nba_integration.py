import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsipy import utils
from sportsipy.nba.constants import SEASON_PAGE_URL
from sportsipy.nba.teams import Team, Teams


MONTH = 1
YEAR = 2021


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
            if div == 'div#div_totals-team':
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
            'rank': 27,
            'abbreviation': 'DET',
            'name': 'Detroit Pistons',
            'games_played': 72,
            'minutes_played': 17430,
            'field_goals': 2783,
            'field_goal_attempts': 6162,
            'field_goal_percentage': .452,
            'three_point_field_goals': 832,
            'three_point_field_goal_attempts': 2370,
            'three_point_field_goal_percentage': .351,
            'two_point_field_goals': 1951,
            'two_point_field_goal_attempts': 3792,
            'two_point_field_goal_percentage': .515,
            'free_throws': 1278,
            'free_throw_attempts': 1683,
            'free_throw_percentage': .759,
            'offensive_rebounds': 694,
            'defensive_rebounds': 2381,
            'total_rebounds': 3075,
            'assists': 1743,
            'steals': 531,
            'blocks': 371,
            'turnovers': 1075,
            'personal_fouls': 1477,
            'points': 7676,
            'opp_field_goals': 2980,
            'opp_field_goal_attempts': 6260,
            'opp_field_goal_percentage': .476,
            'opp_three_point_field_goals': 817,
            'opp_three_point_field_goal_attempts': 2260,
            'opp_three_point_field_goal_percentage': .362,
            'opp_two_point_field_goals': 2163,
            'opp_two_point_field_goal_attempts': 4000,
            'opp_two_point_field_goal_percentage': .541,
            'opp_free_throws': 1221,
            'opp_free_throw_attempts': 1607,
            'opp_free_throw_percentage': .760,
            'opp_offensive_rebounds': 717,
            'opp_defensive_rebounds': 2475,
            'opp_total_rebounds': 3192,
            'opp_assists': 1785,
            'opp_steals': 578,
            'opp_blocks': 419,
            'opp_turnovers': 1004,
            'opp_personal_fouls': 1469,
            'opp_points': 7998
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

    def test_pulling_team_directly(self):
        detroit = Team('DET')

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_team_string_representation(self):
        detroit = Team('DET')

        assert detroit.__repr__() == 'Detroit Pistons (DET) - 2021'

    def test_teams_string_representation(self):
        expected = """Milwaukee Bucks (MIL)
Brooklyn Nets (BRK)
Washington Wizards (WAS)
Utah Jazz (UTA)
Portland Trail Blazers (POR)
Indiana Pacers (IND)
Phoenix Suns (PHO)
Denver Nuggets (DEN)
New Orleans Pelicans (NOP)
Los Angeles Clippers (LAC)
Sacramento Kings (SAC)
Golden State Warriors (GSW)
Atlanta Hawks (ATL)
Philadelphia 76ers (PHI)
Memphis Grizzlies (MEM)
Boston Celtics (BOS)
Dallas Mavericks (DAL)
Minnesota Timberwolves (MIN)
Toronto Raptors (TOR)
San Antonio Spurs (SAS)
Chicago Bulls (CHI)
Los Angeles Lakers (LAL)
Charlotte Hornets (CHO)
Houston Rockets (HOU)
Miami Heat (MIA)
New York Knicks (NYK)
Detroit Pistons (DET)
Oklahoma City Thunder (OKC)
Orlando Magic (ORL)
Cleveland Cavaliers (CLE)"""

        teams = Teams()

        assert teams.__repr__() == expected


class TestNBAIntegrationInvalidDate:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2022)

        teams = Teams()

        for team in teams:
            assert team._year == '2021'
