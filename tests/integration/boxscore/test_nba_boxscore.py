import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import AWAY
from sportsipy.nba.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsipy.nba.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2020

BOXSCORE = '202002220UTA'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (2, 22, YEAR):
        return MockPQ(read_file('boxscores-2-22-2020.html'))
    if url == BOXSCORES_URL % (2, 23, YEAR):
        return MockPQ(read_file('boxscores-2-23-2020.html'))
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
            'date': '9:00 PM, February 22, 2020',
            'location': 'Vivint Smart Home Arena, Salt Lake City, Utah',
            'winner': AWAY,
            'winning_name': 'Houston Rockets',
            'winning_abbr': 'HOU',
            'losing_name': 'Utah Jazz',
            'losing_abbr': 'UTA',
            'pace': 103.2,
            'away_wins': 36,
            'away_losses': 20,
            'away_minutes_played': 240,
            'away_field_goals': 45,
            'away_field_goal_attempts': 92,
            'away_field_goal_percentage': .489,
            'away_two_point_field_goals': 25,
            'away_two_point_field_goal_attempts': 44,
            'away_two_point_field_goal_percentage': .568,
            'away_three_point_field_goals': 20,
            'away_three_point_field_goal_attempts': 48,
            'away_three_point_field_goal_percentage': .417,
            'away_free_throws': 10,
            'away_free_throw_attempts': 14,
            'away_free_throw_percentage': .714,
            'away_offensive_rebounds': 6,
            'away_defensive_rebounds': 36,
            'away_total_rebounds': 42,
            'away_assists': 20,
            'away_steals': 9,
            'away_blocks': 5,
            'away_turnovers': 10,
            'away_personal_fouls': 25,
            'away_points': 120,
            'away_true_shooting_percentage': .611,
            'away_effective_field_goal_percentage': .598,
            'away_three_point_attempt_rate': .522,
            'away_free_throw_attempt_rate': .152,
            'away_offensive_rebound_percentage': 13.0,
            'away_defensive_rebound_percentage': 85.7,
            'away_total_rebound_percentage': 47.7,
            'away_assist_percentage': 44.4,
            'away_steal_percentage': 8.7,
            'away_block_percentage': 8.5,
            'away_turnover_percentage': 9.2,
            'away_offensive_rating': 116.3,
            'away_defensive_rating': 106.6,
            'home_wins': 0,
            'home_losses': 0,
            'home_minutes_played': 240,
            'home_field_goals': 42,
            'home_field_goal_attempts': 90,
            'home_field_goal_percentage': .467,
            'home_two_point_field_goals': 35,
            'home_two_point_field_goal_attempts': 59,
            'home_two_point_field_goal_percentage': .593,
            'home_three_point_field_goals': 7,
            'home_three_point_field_goal_attempts': 31,
            'home_three_point_field_goal_percentage': .226,
            'home_free_throws': 19,
            'home_free_throw_attempts': 24,
            'home_free_throw_percentage': .792,
            'home_offensive_rebounds': 6,
            'home_defensive_rebounds': 40,
            'home_total_rebounds': 46,
            'home_assists': 18,
            'home_steals': 1,
            'home_blocks': 2,
            'home_turnovers': 13,
            'home_personal_fouls': 14,
            'home_points': 110,
            'home_true_shooting_percentage': .547,
            'home_effective_field_goal_percentage': .506,
            'home_three_point_attempt_rate': .344,
            'home_free_throw_attempt_rate': .267,
            'home_offensive_rebound_percentage': 14.3,
            'home_defensive_rebound_percentage': 87.0,
            'home_total_rebound_percentage': 52.3,
            'home_assist_percentage': 42.9,
            'home_steal_percentage': 1.0,
            'home_block_percentage': 4.5,
            'home_turnover_percentage': 11.4,
            'home_offensive_rating': 106.6,
            'home_defensive_rating': 116.3
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nba_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
        assert getattr(self.boxscore, 'summary') == {
            'away': [38, 24, 38, 20],
            'home': [36, 30, 19, 25]
        }

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

    def test_nba_boxscore_string_representation(self):
        expected = ('Boxscore for Houston Rockets at Utah Jazz '
                    '(9:00 PM, February 22, 2020)')

        boxscore = Boxscore(BOXSCORE)

        assert boxscore.__repr__() == expected

    def test_nba_boxscore_home_win_and_losses(self):
        self.boxscore._home_record = '36-20'

        assert self.boxscore.home_wins == 36
        assert self.boxscore.home_losses == 20


class TestNBABoxscores:
    def setup_method(self):
        self.expected = {
            '2-22-2020': [
                {'home_name': 'Atlanta',
                 'home_abbr': 'ATL',
                 'home_score': 111,
                 'boxscore': '202002220ATL',
                 'away_name': 'Dallas',
                 'away_abbr': 'DAL',
                 'away_score': 107,
                 'winning_name': 'Atlanta',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Dallas',
                 'losing_abbr': 'DAL'},
                {'home_name': 'Chicago',
                 'home_abbr': 'CHI',
                 'home_score': 104,
                 'boxscore': '202002220CHI',
                 'away_name': 'Phoenix',
                 'away_abbr': 'PHO',
                 'away_score': 112,
                 'winning_name': 'Phoenix',
                 'winning_abbr': 'PHO',
                 'losing_name': 'Chicago',
                 'losing_abbr': 'CHI'},
                {'home_name': 'Charlotte',
                 'home_abbr': 'CHO',
                 'home_score': 86,
                 'boxscore': '202002220CHO',
                 'away_name': 'Brooklyn',
                 'away_abbr': 'BRK',
                 'away_score': 115,
                 'winning_name': 'Brooklyn',
                 'winning_abbr': 'BRK',
                 'losing_name': 'Charlotte',
                 'losing_abbr': 'CHO'},
                {'home_name': 'LA Clippers',
                 'home_abbr': 'LAC',
                 'home_score': 103,
                 'boxscore': '202002220LAC',
                 'away_name': 'Sacramento',
                 'away_abbr': 'SAC',
                 'away_score': 112,
                 'winning_name': 'Sacramento',
                 'winning_abbr': 'SAC',
                 'losing_name': 'LA Clippers',
                 'losing_abbr': 'LAC'},
                {'home_name': 'Miami',
                 'home_abbr': 'MIA',
                 'home_score': 124,
                 'boxscore': '202002220MIA',
                 'away_name': 'Cleveland',
                 'away_abbr': 'CLE',
                 'away_score': 105,
                 'winning_name': 'Miami',
                 'winning_abbr': 'MIA',
                 'losing_name': 'Cleveland',
                 'losing_abbr': 'CLE'},
                {'home_name': 'Milwaukee',
                 'home_abbr': 'MIL',
                 'home_score': 119,
                 'boxscore': '202002220MIL',
                 'away_name': 'Philadelphia',
                 'away_abbr': 'PHI',
                 'away_score': 98,
                 'winning_name': 'Milwaukee',
                 'winning_abbr': 'MIL',
                 'losing_name': 'Philadelphia',
                 'losing_abbr': 'PHI'},
                {'home_name': 'Utah',
                 'home_abbr': 'UTA',
                 'home_score': 110,
                 'boxscore': '202002220UTA',
                 'away_name': 'Houston',
                 'away_abbr': 'HOU',
                 'away_score': 120,
                 'winning_name': 'Houston',
                 'winning_abbr': 'HOU',
                 'losing_name': 'Utah',
                 'losing_abbr': 'UTA'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 2, 22)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 2, 22), datetime(2020, 2, 21)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_days(self, *args, **kwargs):
        expected = {
            '2-22-2020': [
                {'home_name': 'Atlanta',
                 'home_abbr': 'ATL',
                 'home_score': 111,
                 'boxscore': '202002220ATL',
                 'away_name': 'Dallas',
                 'away_abbr': 'DAL',
                 'away_score': 107,
                 'winning_name': 'Atlanta',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Dallas',
                 'losing_abbr': 'DAL'},
                {'home_name': 'Chicago',
                 'home_abbr': 'CHI',
                 'home_score': 104,
                 'boxscore': '202002220CHI',
                 'away_name': 'Phoenix',
                 'away_abbr': 'PHO',
                 'away_score': 112,
                 'winning_name': 'Phoenix',
                 'winning_abbr': 'PHO',
                 'losing_name': 'Chicago',
                 'losing_abbr': 'CHI'},
                {'home_name': 'Charlotte',
                 'home_abbr': 'CHO',
                 'home_score': 86,
                 'boxscore': '202002220CHO',
                 'away_name': 'Brooklyn',
                 'away_abbr': 'BRK',
                 'away_score': 115,
                 'winning_name': 'Brooklyn',
                 'winning_abbr': 'BRK',
                 'losing_name': 'Charlotte',
                 'losing_abbr': 'CHO'},
                {'home_name': 'LA Clippers',
                 'home_abbr': 'LAC',
                 'home_score': 103,
                 'boxscore': '202002220LAC',
                 'away_name': 'Sacramento',
                 'away_abbr': 'SAC',
                 'away_score': 112,
                 'winning_name': 'Sacramento',
                 'winning_abbr': 'SAC',
                 'losing_name': 'LA Clippers',
                 'losing_abbr': 'LAC'},
                {'home_name': 'Miami',
                 'home_abbr': 'MIA',
                 'home_score': 124,
                 'boxscore': '202002220MIA',
                 'away_name': 'Cleveland',
                 'away_abbr': 'CLE',
                 'away_score': 105,
                 'winning_name': 'Miami',
                 'winning_abbr': 'MIA',
                 'losing_name': 'Cleveland',
                 'losing_abbr': 'CLE'},
                {'home_name': 'Milwaukee',
                 'home_abbr': 'MIL',
                 'home_score': 119,
                 'boxscore': '202002220MIL',
                 'away_name': 'Philadelphia',
                 'away_abbr': 'PHI',
                 'away_score': 98,
                 'winning_name': 'Milwaukee',
                 'winning_abbr': 'MIL',
                 'losing_name': 'Philadelphia',
                 'losing_abbr': 'PHI'},
                {'home_name': 'Utah',
                 'home_abbr': 'UTA',
                 'home_score': 110,
                 'boxscore': '202002220UTA',
                 'away_name': 'Houston',
                 'away_abbr': 'HOU',
                 'away_score': 120,
                 'winning_name': 'Houston',
                 'winning_abbr': 'HOU',
                 'losing_name': 'Utah',
                 'losing_abbr': 'UTA'}
            ],
            '2-23-2020': [
                {'boxscore': '202002230CHI',
                 'away_name': 'Washington',
                 'away_abbr': 'WAS',
                 'away_score': 117,
                 'home_name': 'Chicago',
                 'home_abbr': 'CHI',
                 'home_score': 126,
                 'winning_name': 'Chicago',
                 'winning_abbr': 'CHI',
                 'losing_name': 'Washington',
                 'losing_abbr': 'WAS'},
                {'boxscore': '202002230DEN',
                 'away_name': 'Minnesota',
                 'away_abbr': 'MIN',
                 'away_score': 116,
                 'home_name': 'Denver',
                 'home_abbr': 'DEN',
                 'home_score': 128,
                 'winning_name': 'Denver',
                 'winning_abbr': 'DEN',
                 'losing_name': 'Minnesota',
                 'losing_abbr': 'MIN'},
                {'boxscore': '202002230GSW',
                 'away_name': 'New Orleans',
                 'away_abbr': 'NOP',
                 'away_score': 115,
                 'home_name': 'Golden State',
                 'home_abbr': 'GSW',
                 'home_score': 101,
                 'winning_name': 'New Orleans',
                 'winning_abbr': 'NOP',
                 'losing_name': 'Golden State',
                 'losing_abbr': 'GSW'},
                {'boxscore': '202002230LAL',
                 'away_name': 'Boston',
                 'away_abbr': 'BOS',
                 'away_score': 112,
                 'home_name': 'LA Lakers',
                 'home_abbr': 'LAL',
                 'home_score': 114,
                 'winning_name': 'LA Lakers',
                 'winning_abbr': 'LAL',
                 'losing_name': 'Boston',
                 'losing_abbr': 'BOS'},
                {'boxscore': '202002230OKC',
                 'away_name': 'San Antonio',
                 'away_abbr': 'SAS',
                 'away_score': 103,
                 'home_name': 'Oklahoma City',
                 'home_abbr': 'OKC',
                 'home_score': 131,
                 'winning_name': 'Oklahoma City',
                 'winning_abbr': 'OKC',
                 'losing_name': 'San Antonio',
                 'losing_abbr': 'SAS'},
                {'boxscore': '202002230POR',
                 'away_name': 'Detroit',
                 'away_abbr': 'DET',
                 'away_score': 104,
                 'home_name': 'Portland',
                 'home_abbr': 'POR',
                 'home_score': 107,
                 'winning_name': 'Portland',
                 'winning_abbr': 'POR',
                 'losing_name': 'Detroit',
                 'losing_abbr': 'DET'},
                {'boxscore': '202002230TOR',
                 'away_name': 'Indiana',
                 'away_abbr': 'IND',
                 'away_score': 81,
                 'home_name': 'Toronto',
                 'home_abbr': 'TOR',
                 'home_score': 127,
                 'winning_name': 'Toronto',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Indiana',
                 'losing_abbr': 'IND'}
            ]
        }
        result = Boxscores(datetime(2020, 2, 22), datetime(2020, 2, 23)).games

        assert result == expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 2, 22))

        assert result.__repr__() == 'NBA games for 2-22-2020'
