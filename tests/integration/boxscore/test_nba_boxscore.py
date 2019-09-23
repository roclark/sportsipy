import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import HOME
from sportsreference.nba.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsreference.nba.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2017

BOXSCORE = '201710310LAL'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (2, 4, YEAR):
        return MockPQ(read_file('boxscores-2-4-2017.html'))
    if url == BOXSCORES_URL % (2, 5, YEAR):
        return MockPQ(read_file('boxscores-2-5-2017.html'))
    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNBABoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': '10:30 PM, October 31, 2017',
            'location': 'STAPLES Center, Los Angeles, California',
            'winner': HOME,
            'winning_name': 'Los Angeles Lakers',
            'winning_abbr': 'LAL',
            'losing_name': 'Detroit Pistons',
            'losing_abbr': 'DET',
            'pace': 97.4,
            'away_wins': 5,
            'away_losses': 3,
            'away_minutes_played': 240,
            'away_field_goals': 41,
            'away_field_goal_attempts': 94,
            'away_field_goal_percentage': .436,
            'away_two_point_field_goals': 31,
            'away_two_point_field_goal_attempts': 61,
            'away_two_point_field_goal_percentage': .508,
            'away_three_point_field_goals': 10,
            'away_three_point_field_goal_attempts': 33,
            'away_three_point_field_goal_percentage': .303,
            'away_free_throws': 1,
            'away_free_throw_attempts': 3,
            'away_free_throw_percentage': .333,
            'away_offensive_rebounds': 10,
            'away_defensive_rebounds': 34,
            'away_total_rebounds': 44,
            'away_assists': 21,
            'away_steals': 7,
            'away_blocks': 3,
            'away_turnovers': 12,
            'away_personal_fouls': 11,
            'away_points': 93,
            'away_true_shooting_percentage': .488,
            'away_effective_field_goal_percentage': .489,
            'away_three_point_attempt_rate': .351,
            'away_free_throw_attempt_rate': .032,
            'away_offensive_rebound_percentage': 19.2,
            'away_defensive_rebound_percentage': 75.6,
            'away_total_rebound_percentage': 45.4,
            'away_assist_percentage': 51.2,
            'away_steal_percentage': 7.2,
            'away_block_percentage': 4.6,
            'away_turnover_percentage': 11.2,
            'away_offensive_rating': 95.5,
            'away_defensive_rating': 116.0,
            'home_wins': 3,
            'home_losses': 4,
            'home_minutes_played': 240,
            'home_field_goals': 45,
            'home_field_goal_attempts': 91,
            'home_field_goal_percentage': .495,
            'home_two_point_field_goals': 33,
            'home_two_point_field_goal_attempts': 65,
            'home_two_point_field_goal_percentage': .508,
            'home_three_point_field_goals': 12,
            'home_three_point_field_goal_attempts': 26,
            'home_three_point_field_goal_percentage': .462,
            'home_free_throws': 11,
            'home_free_throw_attempts': 14,
            'home_free_throw_percentage': .786,
            'home_offensive_rebounds': 11,
            'home_defensive_rebounds': 42,
            'home_total_rebounds': 53,
            'home_assists': 30,
            'home_steals': 9,
            'home_blocks': 5,
            'home_turnovers': 14,
            'home_personal_fouls': 14,
            'home_points': 113,
            'home_true_shooting_percentage': .582,
            'home_effective_field_goal_percentage': .560,
            'home_three_point_attempt_rate': .286,
            'home_free_throw_attempt_rate': .154,
            'home_offensive_rebound_percentage': 24.4,
            'home_defensive_rebound_percentage': 80.8,
            'home_total_rebound_percentage': 54.6,
            'home_assist_percentage': 66.7,
            'home_steal_percentage': 9.2,
            'home_block_percentage': 8.2,
            'home_turnover_percentage': 12.6,
            'home_offensive_rating': 116.0,
            'home_defensive_rating': 95.5
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nba_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            if key == '_uri':
                continue
            assert value is None

    def test_nba_boxscore_dataframe_returns_dataframe_of_all_values(self):
        df = pd.DataFrame([self.results], index=[BOXSCORE])

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, self.boxscore.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nba_boxscore_players(self):
        assert len(self.boxscore.home_players) == 13
        assert len(self.boxscore.away_players) == 13

        for player in self.boxscore.home_players:
            assert not player.dataframe.empty
        for player in self.boxscore.away_players:
            assert not player.dataframe.empty


class TestNBABoxscores:
    def setup_method(self):
        self.expected = {
            '2-4-2017': [
                {'home_name': 'Atlanta',
                 'home_abbr': 'ATL',
                 'home_score': 113,
                 'boxscore': '201702040ATL',
                 'away_name': 'Orlando',
                 'away_abbr': 'ORL',
                 'away_score': 86,
                 'winning_name': 'Atlanta',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Orlando',
                 'losing_abbr': 'ORL'},
                {'home_name': 'Indiana',
                 'home_abbr': 'IND',
                 'home_score': 105,
                 'boxscore': '201702040IND',
                 'away_name': 'Detroit',
                 'away_abbr': 'DET',
                 'away_score': 84,
                 'winning_name': 'Indiana',
                 'winning_abbr': 'IND',
                 'losing_name': 'Detroit',
                 'losing_abbr': 'DET'},
                {'home_name': 'Miami',
                 'home_abbr': 'MIA',
                 'home_score': 125,
                 'boxscore': '201702040MIA',
                 'away_name': 'Philadelphia',
                 'away_abbr': 'PHI',
                 'away_score': 102,
                 'winning_name': 'Miami',
                 'winning_abbr': 'MIA',
                 'losing_name': 'Philadelphia',
                 'losing_abbr': 'PHI'},
                {'home_name': 'Minnesota',
                 'home_abbr': 'MIN',
                 'home_score': 99,
                 'boxscore': '201702040MIN',
                 'away_name': 'Memphis',
                 'away_abbr': 'MEM',
                 'away_score': 107,
                 'winning_name': 'Memphis',
                 'winning_abbr': 'MEM',
                 'losing_name': 'Minnesota',
                 'losing_abbr': 'MIN'},
                {'home_name': 'New York',
                 'home_abbr': 'NYK',
                 'home_score': 104,
                 'boxscore': '201702040NYK',
                 'away_name': 'Cleveland',
                 'away_abbr': 'CLE',
                 'away_score': 111,
                 'winning_name': 'Cleveland',
                 'winning_abbr': 'CLE',
                 'losing_name': 'New York',
                 'losing_abbr': 'NYK'},
                {'home_name': 'Phoenix',
                 'home_abbr': 'PHO',
                 'home_score': 112,
                 'boxscore': '201702040PHO',
                 'away_name': 'Milwaukee',
                 'away_abbr': 'MIL',
                 'away_score': 137,
                 'winning_name': 'Milwaukee',
                 'winning_abbr': 'MIL',
                 'losing_name': 'Phoenix',
                 'losing_abbr': 'PHO'},
                {'home_name': 'Sacramento',
                 'home_abbr': 'SAC',
                 'home_score': 109,
                 'boxscore': '201702040SAC',
                 'away_name': 'Golden State',
                 'away_abbr': 'GSW',
                 'away_score': 106,
                 'winning_name': 'Sacramento',
                 'winning_abbr': 'SAC',
                 'losing_name': 'Golden State',
                 'losing_abbr': 'GSW'},
                {'home_name': 'San Antonio',
                 'home_abbr': 'SAS',
                 'home_score': 121,
                 'boxscore': '201702040SAS',
                 'away_name': 'Denver',
                 'away_abbr': 'DEN',
                 'away_score': 97,
                 'winning_name': 'San Antonio',
                 'winning_abbr': 'SAS',
                 'losing_name': 'Denver',
                 'losing_abbr': 'DEN'},
                {'home_name': 'Utah',
                 'home_abbr': 'UTA',
                 'home_score': 105,
                 'boxscore': '201702040UTA',
                 'away_name': 'Charlotte',
                 'away_abbr': 'CHO',
                 'away_score': 98,
                 'winning_name': 'Utah',
                 'winning_abbr': 'UTA',
                 'losing_name': 'Charlotte',
                 'losing_abbr': 'CHO'},
                {'home_name': 'Washington',
                 'home_abbr': 'WAS',
                 'home_score': 105,
                 'boxscore': '201702040WAS',
                 'away_name': 'New Orleans',
                 'away_abbr': 'NOP',
                 'away_score': 91,
                 'winning_name': 'Washington',
                 'winning_abbr': 'WAS',
                 'losing_name': 'New Orleans',
                 'losing_abbr': 'NOP'},
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2017, 2, 4)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 3)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_days(self, *args, **kwargs):
        expected = {
            '2-4-2017': [
                {'boxscore': '201702040ATL',
                 'away_name': 'Orlando',
                 'away_abbr': 'ORL',
                 'away_score': 86,
                 'home_name': 'Atlanta',
                 'home_abbr': 'ATL',
                 'home_score': 113,
                 'winning_name': 'Atlanta',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Orlando',
                 'losing_abbr': 'ORL'},
                {'boxscore': '201702040IND',
                 'away_name': 'Detroit',
                 'away_abbr': 'DET',
                 'away_score': 84,
                 'home_name': 'Indiana',
                 'home_abbr': 'IND',
                 'home_score': 105,
                 'winning_name': 'Indiana',
                 'winning_abbr': 'IND',
                 'losing_name': 'Detroit',
                 'losing_abbr': 'DET'},
                {'boxscore': '201702040MIA',
                 'away_name': 'Philadelphia',
                 'away_abbr': 'PHI',
                 'away_score': 102,
                 'home_name': 'Miami',
                 'home_abbr': 'MIA',
                 'home_score': 125,
                 'winning_name': 'Miami',
                 'winning_abbr': 'MIA',
                 'losing_name': 'Philadelphia',
                 'losing_abbr': 'PHI'},
                {'boxscore': '201702040MIN',
                 'away_name': 'Memphis',
                 'away_abbr': 'MEM',
                 'away_score': 107,
                 'home_name': 'Minnesota',
                 'home_abbr': 'MIN',
                 'home_score': 99,
                 'winning_name': 'Memphis',
                 'winning_abbr': 'MEM',
                 'losing_name': 'Minnesota',
                 'losing_abbr': 'MIN'},
                {'boxscore': '201702040NYK',
                 'away_name': 'Cleveland',
                 'away_abbr': 'CLE',
                 'away_score': 111,
                 'home_name': 'New York',
                 'home_abbr': 'NYK',
                 'home_score': 104,
                 'winning_name': 'Cleveland',
                 'winning_abbr': 'CLE',
                 'losing_name': 'New York',
                 'losing_abbr': 'NYK'},
                {'boxscore': '201702040PHO',
                 'away_name': 'Milwaukee',
                 'away_abbr': 'MIL',
                 'away_score': 137,
                 'home_name': 'Phoenix',
                 'home_abbr': 'PHO',
                 'home_score': 112,
                 'winning_name': 'Milwaukee',
                 'winning_abbr': 'MIL',
                 'losing_name': 'Phoenix',
                 'losing_abbr': 'PHO'},
                {'boxscore': '201702040SAC',
                 'away_name': 'Golden State',
                 'away_abbr': 'GSW',
                 'away_score': 106,
                 'home_name': 'Sacramento',
                 'home_abbr': 'SAC',
                 'home_score': 109,
                 'winning_name': 'Sacramento',
                 'winning_abbr': 'SAC',
                 'losing_name': 'Golden State',
                 'losing_abbr': 'GSW'},
                {'boxscore': '201702040SAS',
                 'away_name': 'Denver',
                 'away_abbr': 'DEN',
                 'away_score': 97,
                 'home_name': 'San Antonio',
                 'home_abbr': 'SAS',
                 'home_score': 121,
                 'winning_name': 'San Antonio',
                 'winning_abbr': 'SAS',
                 'losing_name': 'Denver',
                 'losing_abbr': 'DEN'},
                {'boxscore': '201702040UTA',
                 'away_name': 'Charlotte',
                 'away_abbr': 'CHO',
                 'away_score': 98,
                 'home_name': 'Utah',
                 'home_abbr': 'UTA',
                 'home_score': 105,
                 'winning_name': 'Utah',
                 'winning_abbr': 'UTA',
                 'losing_name': 'Charlotte',
                 'losing_abbr': 'CHO'},
                {'boxscore': '201702040WAS',
                 'away_name': 'New Orleans',
                 'away_abbr': 'NOP',
                 'away_score': 91,
                 'home_name': 'Washington',
                 'home_abbr': 'WAS',
                 'home_score': 105,
                 'winning_name': 'Washington',
                 'winning_abbr': 'WAS',
                 'losing_name': 'New Orleans',
                 'losing_abbr': 'NOP'}
            ],
            '2-5-2017': [
                {'boxscore': '201702050BOS',
                 'away_name': 'LA Clippers',
                 'away_abbr': 'LAC',
                 'away_score': 102,
                 'home_name': 'Boston',
                 'home_abbr': 'BOS',
                 'home_score': 107,
                 'winning_name': 'Boston',
                 'winning_abbr': 'BOS',
                 'losing_name': 'LA Clippers',
                 'losing_abbr': 'LAC'},
                {'boxscore': '201702050BRK',
                 'away_name': 'Toronto',
                 'away_abbr': 'TOR',
                 'away_score': 103,
                 'home_name': 'Brooklyn',
                 'home_abbr': 'BRK',
                 'home_score': 95,
                 'winning_name': 'Toronto',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Brooklyn',
                 'losing_abbr': 'BRK'},
                {'boxscore': '201702050OKC',
                 'away_name': 'Portland',
                 'away_abbr': 'POR',
                 'away_score': 99,
                 'home_name': 'Oklahoma City',
                 'home_abbr': 'OKC',
                 'home_score': 105,
                 'winning_name': 'Oklahoma City',
                 'winning_abbr': 'OKC',
                 'losing_name': 'Portland',
                 'losing_abbr': 'POR'}
            ]
        }
        result = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 5)).games

        assert result == expected
