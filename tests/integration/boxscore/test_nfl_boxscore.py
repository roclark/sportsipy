import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import HOME
from sportsipy.nfl.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsipy.nfl.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2020

BOXSCORE = '202009100kan'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (YEAR, 1):
        return MockPQ(read_file('boxscores-1-2020.html'))
    if url == BOXSCORES_URL % (YEAR, 2):
        return MockPQ(read_file('boxscores-2-2020.html'))
    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNFLBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Thursday Sep 10, 2020',
            'time': '8:20pm',
            'datetime': datetime(2020, 9, 10, 20, 20),
            'stadium': 'Arrowhead Stadium',
            'attendance': 15895,
            'duration': '2:53',
            'winner': HOME,
            'winning_name': 'Kansas City Chiefs',
            'winning_abbr': 'KAN',
            'losing_name': 'Houston Texans',
            'losing_abbr': 'HTX',
            'won_toss': 'Chiefs (deferred)',
            'weather': '56 degrees, relative humidity 95%, wind 7 mph',
            'vegas_line': 'Kansas City Chiefs -9.5',
            'surface': 'Astroturf',
            'roof': 'Outdoors',
            'over_under': '53.5 (over)',
            'away_points': 20,
            'away_first_downs': 21,
            'away_rush_attempts': 22,
            'away_rush_yards': 118,
            'away_rush_touchdowns': 2,
            'away_pass_completions': 20,
            'away_pass_attempts': 32,
            'away_pass_yards': 253,
            'away_pass_touchdowns': 1,
            'away_interceptions': 1,
            'away_times_sacked': 4,
            'away_yards_lost_from_sacks': 11,
            'away_net_pass_yards': 242,
            'away_total_yards': 360,
            'away_fumbles': 0,
            'away_fumbles_lost': 0,
            'away_turnovers': 1,
            'away_penalties': 5,
            'away_yards_from_penalties': 37,
            'away_third_down_conversions': 4,
            'away_third_down_attempts': 10,
            'away_fourth_down_conversions': 1,
            'away_fourth_down_attempts': 1,
            'away_time_of_possession': '25:13',
            'home_points': 34,
            'home_first_downs': 28,
            'home_rush_attempts': 34,
            'home_rush_yards': 166,
            'home_rush_touchdowns': 1,
            'home_pass_completions': 24,
            'home_pass_attempts': 32,
            'home_pass_yards': 211,
            'home_pass_touchdowns': 3,
            'home_interceptions': 0,
            'home_times_sacked': 1,
            'home_yards_lost_from_sacks': 8,
            'home_net_pass_yards': 203,
            'home_total_yards': 369,
            'home_fumbles': 0,
            'home_fumbles_lost': 0,
            'home_turnovers': 0,
            'home_penalties': 1,
            'home_yards_from_penalties': 5,
            'home_third_down_conversions': 7,
            'home_third_down_attempts': 13,
            'home_fourth_down_conversions': 1,
            'home_fourth_down_attempts': 1,
            'home_time_of_possession': '34:47',
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nfl_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
        assert getattr(self.boxscore, 'summary') == {
            'away': [7, 0, 0, 13],
            'home': [0, 17, 7, 10]
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

    def test_nfl_boxscore_dataframe_returns_dataframe_of_all_values(self):
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

    def test_nfl_boxscore_players(self):
        boxscore = Boxscore(BOXSCORE)

        assert len(boxscore.home_players) == 33
        assert len(boxscore.away_players) == 28

        for player in boxscore.home_players:
            assert not player.dataframe.empty
        for player in boxscore.away_players:
            assert not player.dataframe.empty

    def test_nfl_boxscore_string_representation(self):
        expected = ('Boxscore for Houston Texans at Kansas City Chiefs '
                    '(Thursday Sep 10, 2020)')

        boxscore = Boxscore(BOXSCORE)

        assert boxscore.__repr__() == expected


class TestNFLBoxscores:
    def setup_method(self):
        self.expected = {
            '1-2020': [
                {'boxscore': '202009100kan',
                 'away_name': 'Houston Texans',
                 'away_abbr': 'htx',
                 'away_score': 20,
                 'home_name': 'Kansas City Chiefs',
                 'home_abbr': 'kan',
                 'home_score': 34,
                 'winning_name': 'Kansas City Chiefs',
                 'winning_abbr': 'kan',
                 'losing_name': 'Houston Texans',
                 'losing_abbr': 'htx'},
                {'boxscore': '202009130buf',
                 'away_name': 'New York Jets',
                 'away_abbr': 'nyj',
                 'away_score': 17,
                 'home_name': 'Buffalo Bills',
                 'home_abbr': 'buf',
                 'home_score': 27,
                 'winning_name': 'Buffalo Bills',
                 'winning_abbr': 'buf',
                 'losing_name': 'New York Jets',
                 'losing_abbr': 'nyj'},
                {'boxscore': '202009130atl',
                 'away_name': 'Seattle Seahawks',
                 'away_abbr': 'sea',
                 'away_score': 38,
                 'home_name': 'Atlanta Falcons',
                 'home_abbr': 'atl',
                 'home_score': 25,
                 'winning_name': 'Seattle Seahawks',
                 'winning_abbr': 'sea',
                 'losing_name': 'Atlanta Falcons',
                 'losing_abbr': 'atl'},
                {'boxscore': '202009130was',
                 'away_name': 'Philadelphia Eagles',
                 'away_abbr': 'phi',
                 'away_score': 17,
                 'home_name': 'Washington Football Team',
                 'home_abbr': 'was',
                 'home_score': 27,
                 'winning_name': 'Washington Football Team',
                 'winning_abbr': 'was',
                 'losing_name': 'Philadelphia Eagles',
                 'losing_abbr': 'phi'},
                {'boxscore': '202009130rav',
                 'away_name': 'Cleveland Browns',
                 'away_abbr': 'cle',
                 'away_score': 6,
                 'home_name': 'Baltimore Ravens',
                 'home_abbr': 'rav',
                 'home_score': 38,
                 'winning_name': 'Baltimore Ravens',
                 'winning_abbr': 'rav',
                 'losing_name': 'Cleveland Browns',
                 'losing_abbr': 'cle'},
                {'boxscore': '202009130nwe',
                 'away_name': 'Miami Dolphins',
                 'away_abbr': 'mia',
                 'away_score': 11,
                 'home_name': 'New England Patriots',
                 'home_abbr': 'nwe',
                 'home_score': 21,
                 'winning_name': 'New England Patriots',
                 'winning_abbr': 'nwe',
                 'losing_name': 'Miami Dolphins',
                 'losing_abbr': 'mia'},
                {'boxscore': '202009130min',
                 'away_name': 'Green Bay Packers',
                 'away_abbr': 'gnb',
                 'away_score': 43,
                 'home_name': 'Minnesota Vikings',
                 'home_abbr': 'min',
                 'home_score': 34,
                 'winning_name': 'Green Bay Packers',
                 'winning_abbr': 'gnb',
                 'losing_name': 'Minnesota Vikings',
                 'losing_abbr': 'min'},
                {'boxscore': '202009130jax',
                 'away_name': 'Indianapolis Colts',
                 'away_abbr': 'clt',
                 'away_score': 20,
                 'home_name': 'Jacksonville Jaguars',
                 'home_abbr': 'jax',
                 'home_score': 27,
                 'winning_name': 'Jacksonville Jaguars',
                 'winning_abbr': 'jax',
                 'losing_name': 'Indianapolis Colts',
                 'losing_abbr': 'clt'},
                {'boxscore': '202009130det',
                 'away_name': 'Chicago Bears',
                 'away_abbr': 'chi',
                 'away_score': 27,
                 'home_name': 'Detroit Lions',
                 'home_abbr': 'det',
                 'home_score': 23,
                 'winning_name': 'Chicago Bears',
                 'winning_abbr': 'chi',
                 'losing_name': 'Detroit Lions',
                 'losing_abbr': 'det'},
                {'boxscore': '202009130car',
                 'away_name': 'Las Vegas Raiders',
                 'away_abbr': 'rai',
                 'away_score': 34,
                 'home_name': 'Carolina Panthers',
                 'home_abbr': 'car',
                 'home_score': 30,
                 'winning_name': 'Las Vegas Raiders',
                 'winning_abbr': 'rai',
                 'losing_name': 'Carolina Panthers',
                 'losing_abbr': 'car'},
                {'boxscore': '202009130cin',
                 'away_name': 'Los Angeles Chargers',
                 'away_abbr': 'sdg',
                 'away_score': 16,
                 'home_name': 'Cincinnati Bengals',
                 'home_abbr': 'cin',
                 'home_score': 13,
                 'winning_name': 'Los Angeles Chargers',
                 'winning_abbr': 'sdg',
                 'losing_name': 'Cincinnati Bengals',
                 'losing_abbr': 'cin'},
                {'boxscore': '202009130sfo',
                 'away_name': 'Arizona Cardinals',
                 'away_abbr': 'crd',
                 'away_score': 24,
                 'home_name': 'San Francisco 49ers',
                 'home_abbr': 'sfo',
                 'home_score': 20,
                 'winning_name': 'Arizona Cardinals',
                 'winning_abbr': 'crd',
                 'losing_name': 'San Francisco 49ers',
                 'losing_abbr': 'sfo'},
                {'boxscore': '202009130nor',
                 'away_name': 'Tampa Bay Buccaneers',
                 'away_abbr': 'tam',
                 'away_score': 23,
                 'home_name': 'New Orleans Saints',
                 'home_abbr': 'nor',
                 'home_score': 34,
                 'winning_name': 'New Orleans Saints',
                 'winning_abbr': 'nor',
                 'losing_name': 'Tampa Bay Buccaneers',
                 'losing_abbr': 'tam'},
                {'boxscore': '202009130ram',
                 'away_name': 'Dallas Cowboys',
                 'away_abbr': 'dal',
                 'away_score': 17,
                 'home_name': 'Los Angeles Rams',
                 'home_abbr': 'ram',
                 'home_score': 20,
                 'winning_name': 'Los Angeles Rams',
                 'winning_abbr': 'ram',
                 'losing_name': 'Dallas Cowboys',
                 'losing_abbr': 'dal'},
                {'boxscore': '202009140nyg',
                 'away_name': 'Pittsburgh Steelers',
                 'away_abbr': 'pit',
                 'away_score': 26,
                 'home_name': 'New York Giants',
                 'home_abbr': 'nyg',
                 'home_score': 16,
                 'winning_name': 'Pittsburgh Steelers',
                 'winning_abbr': 'pit',
                 'losing_name': 'New York Giants',
                 'losing_abbr': 'nyg'},
                {'boxscore': '202009140den',
                 'away_name': 'Tennessee Titans',
                 'away_abbr': 'oti',
                 'away_score': 16,
                 'home_name': 'Denver Broncos',
                 'home_abbr': 'den',
                 'home_score': 14,
                 'winning_name': 'Tennessee Titans',
                 'winning_abbr': 'oti',
                 'losing_name': 'Denver Broncos',
                 'losing_abbr': 'den'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(1, 2020).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(1, 2020, 0).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_weeks(self, *args, **kwargs):
        expected = {
            '1-2020': [
               {'boxscore': '202009100kan',
                'away_name': 'Houston Texans',
                'away_abbr': 'htx',
                'away_score': 20,
                'home_name': 'Kansas City Chiefs',
                'home_abbr': 'kan',
                'home_score': 34,
                'winning_name': 'Kansas City Chiefs',
                'winning_abbr': 'kan',
                'losing_name': 'Houston Texans',
                'losing_abbr': 'htx'},
               {'boxscore': '202009130buf',
                'away_name': 'New York Jets',
                'away_abbr': 'nyj',
                'away_score': 17,
                'home_name': 'Buffalo Bills',
                'home_abbr': 'buf',
                'home_score': 27,
                'winning_name': 'Buffalo Bills',
                'winning_abbr': 'buf',
                'losing_name': 'New York Jets',
                'losing_abbr': 'nyj'},
               {'boxscore': '202009130atl',
                'away_name': 'Seattle Seahawks',
                'away_abbr': 'sea',
                'away_score': 38,
                'home_name': 'Atlanta Falcons',
                'home_abbr': 'atl',
                'home_score': 25,
                'winning_name': 'Seattle Seahawks',
                'winning_abbr': 'sea',
                'losing_name': 'Atlanta Falcons',
                'losing_abbr': 'atl'},
               {'boxscore': '202009130was',
                'away_name': 'Philadelphia Eagles',
                'away_abbr': 'phi',
                'away_score': 17,
                'home_name': 'Washington Football Team',
                'home_abbr': 'was',
                'home_score': 27,
                'winning_name': 'Washington Football Team',
                'winning_abbr': 'was',
                'losing_name': 'Philadelphia Eagles',
                'losing_abbr': 'phi'},
               {'boxscore': '202009130rav',
                'away_name': 'Cleveland Browns',
                'away_abbr': 'cle',
                'away_score': 6,
                'home_name': 'Baltimore Ravens',
                'home_abbr': 'rav',
                'home_score': 38,
                'winning_name': 'Baltimore Ravens',
                'winning_abbr': 'rav',
                'losing_name': 'Cleveland Browns',
                'losing_abbr': 'cle'},
               {'boxscore': '202009130nwe',
                'away_name': 'Miami Dolphins',
                'away_abbr': 'mia',
                'away_score': 11,
                'home_name': 'New England Patriots',
                'home_abbr': 'nwe',
                'home_score': 21,
                'winning_name': 'New England Patriots',
                'winning_abbr': 'nwe',
                'losing_name': 'Miami Dolphins',
                'losing_abbr': 'mia'},
               {'boxscore': '202009130min',
                'away_name': 'Green Bay Packers',
                'away_abbr': 'gnb',
                'away_score': 43,
                'home_name': 'Minnesota Vikings',
                'home_abbr': 'min',
                'home_score': 34,
                'winning_name': 'Green Bay Packers',
                'winning_abbr': 'gnb',
                'losing_name': 'Minnesota Vikings',
                'losing_abbr': 'min'},
               {'boxscore': '202009130jax',
                'away_name': 'Indianapolis Colts',
                'away_abbr': 'clt',
                'away_score': 20,
                'home_name': 'Jacksonville Jaguars',
                'home_abbr': 'jax',
                'home_score': 27,
                'winning_name': 'Jacksonville Jaguars',
                'winning_abbr': 'jax',
                'losing_name': 'Indianapolis Colts',
                'losing_abbr': 'clt'},
               {'boxscore': '202009130det',
                'away_name': 'Chicago Bears',
                'away_abbr': 'chi',
                'away_score': 27,
                'home_name': 'Detroit Lions',
                'home_abbr': 'det',
                'home_score': 23,
                'winning_name': 'Chicago Bears',
                'winning_abbr': 'chi',
                'losing_name': 'Detroit Lions',
                'losing_abbr': 'det'},
               {'boxscore': '202009130car',
                'away_name': 'Las Vegas Raiders',
                'away_abbr': 'rai',
                'away_score': 34,
                'home_name': 'Carolina Panthers',
                'home_abbr': 'car',
                'home_score': 30,
                'winning_name': 'Las Vegas Raiders',
                'winning_abbr': 'rai',
                'losing_name': 'Carolina Panthers',
                'losing_abbr': 'car'},
               {'boxscore': '202009130cin',
                'away_name': 'Los Angeles Chargers',
                'away_abbr': 'sdg',
                'away_score': 16,
                'home_name': 'Cincinnati Bengals',
                'home_abbr': 'cin',
                'home_score': 13,
                'winning_name': 'Los Angeles Chargers',
                'winning_abbr': 'sdg',
                'losing_name': 'Cincinnati Bengals',
                'losing_abbr': 'cin'},
               {'boxscore': '202009130sfo',
                'away_name': 'Arizona Cardinals',
                'away_abbr': 'crd',
                'away_score': 24,
                'home_name': 'San Francisco 49ers',
                'home_abbr': 'sfo',
                'home_score': 20,
                'winning_name': 'Arizona Cardinals',
                'winning_abbr': 'crd',
                'losing_name': 'San Francisco 49ers',
                'losing_abbr': 'sfo'},
               {'boxscore': '202009130nor',
                'away_name': 'Tampa Bay Buccaneers',
                'away_abbr': 'tam',
                'away_score': 23,
                'home_name': 'New Orleans Saints',
                'home_abbr': 'nor',
                'home_score': 34,
                'winning_name': 'New Orleans Saints',
                'winning_abbr': 'nor',
                'losing_name': 'Tampa Bay Buccaneers',
                'losing_abbr': 'tam'},
               {'boxscore': '202009130ram',
                'away_name': 'Dallas Cowboys',
                'away_abbr': 'dal',
                'away_score': 17,
                'home_name': 'Los Angeles Rams',
                'home_abbr': 'ram',
                'home_score': 20,
                'winning_name': 'Los Angeles Rams',
                'winning_abbr': 'ram',
                'losing_name': 'Dallas Cowboys',
                'losing_abbr': 'dal'},
               {'boxscore': '202009140nyg',
                'away_name': 'Pittsburgh Steelers',
                'away_abbr': 'pit',
                'away_score': 26,
                'home_name': 'New York Giants',
                'home_abbr': 'nyg',
                'home_score': 16,
                'winning_name': 'Pittsburgh Steelers',
                'winning_abbr': 'pit',
                'losing_name': 'New York Giants',
                'losing_abbr': 'nyg'},
               {'boxscore': '202009140den',
                'away_name': 'Tennessee Titans',
                'away_abbr': 'oti',
                'away_score': 16,
                'home_name': 'Denver Broncos',
                'home_abbr': 'den',
                'home_score': 14,
                'winning_name': 'Tennessee Titans',
                'winning_abbr': 'oti',
                'losing_name': 'Denver Broncos',
                'losing_abbr': 'den'}
            ],
            '2-2020': [
                {'boxscore': '202009170cle',
                 'away_name': 'Cincinnati Bengals',
                 'away_abbr': 'cin',
                 'away_score': 30,
                 'home_name': 'Cleveland Browns',
                 'home_abbr': 'cle',
                 'home_score': 35,
                 'winning_name': 'Cleveland Browns',
                 'winning_abbr': 'cle',
                 'losing_name': 'Cincinnati Bengals',
                 'losing_abbr': 'cin'},
                {'boxscore': '202009200clt',
                 'away_name': 'Minnesota Vikings',
                 'away_abbr': 'min',
                 'away_score': 11,
                 'home_name': 'Indianapolis Colts',
                 'home_abbr': 'clt',
                 'home_score': 28,
                 'winning_name': 'Indianapolis Colts',
                 'winning_abbr': 'clt',
                 'losing_name': 'Minnesota Vikings',
                 'losing_abbr': 'min'},
                {'boxscore': '202009200chi',
                 'away_name': 'New York Giants',
                 'away_abbr': 'nyg',
                 'away_score': 13,
                 'home_name': 'Chicago Bears',
                 'home_abbr': 'chi',
                 'home_score': 17,
                 'winning_name': 'Chicago Bears',
                 'winning_abbr': 'chi',
                 'losing_name': 'New York Giants',
                 'losing_abbr': 'nyg'},
                {'boxscore': '202009200tam',
                 'away_name': 'Carolina Panthers',
                 'away_abbr': 'car',
                 'away_score': 17,
                 'home_name': 'Tampa Bay Buccaneers',
                 'home_abbr': 'tam',
                 'home_score': 31,
                 'winning_name': 'Tampa Bay Buccaneers',
                 'winning_abbr': 'tam',
                 'losing_name': 'Carolina Panthers',
                 'losing_abbr': 'car'},
                {'boxscore': '202009200pit',
                 'away_name': 'Denver Broncos',
                 'away_abbr': 'den',
                 'away_score': 21,
                 'home_name': 'Pittsburgh Steelers',
                 'home_abbr': 'pit',
                 'home_score': 26,
                 'winning_name': 'Pittsburgh Steelers',
                 'winning_abbr': 'pit',
                 'losing_name': 'Denver Broncos',
                 'losing_abbr': 'den'},
                {'boxscore': '202009200phi',
                 'away_name': 'Los Angeles Rams',
                 'away_abbr': 'ram',
                 'away_score': 37,
                 'home_name': 'Philadelphia Eagles',
                 'home_abbr': 'phi',
                 'home_score': 19,
                 'winning_name': 'Los Angeles Rams',
                 'winning_abbr': 'ram',
                 'losing_name': 'Philadelphia Eagles',
                 'losing_abbr': 'phi'},
                {'boxscore': '202009200oti',
                 'away_name': 'Jacksonville Jaguars',
                 'away_abbr': 'jax',
                 'away_score': 30,
                 'home_name': 'Tennessee Titans',
                 'home_abbr': 'oti',
                 'home_score': 33,
                 'winning_name': 'Tennessee Titans',
                 'winning_abbr': 'oti',
                 'losing_name': 'Jacksonville Jaguars',
                 'losing_abbr': 'jax'},
                {'boxscore': '202009200nyj',
                 'away_name': 'San Francisco 49ers',
                 'away_abbr': 'sfo',
                 'away_score': 31,
                 'home_name': 'New York Jets',
                 'home_abbr': 'nyj',
                 'home_score': 13,
                 'winning_name': 'San Francisco 49ers',
                 'winning_abbr': 'sfo',
                 'losing_name': 'New York Jets',
                 'losing_abbr': 'nyj'},
                {'boxscore': '202009200mia',
                 'away_name': 'Buffalo Bills',
                 'away_abbr': 'buf',
                 'away_score': 31,
                 'home_name': 'Miami Dolphins',
                 'home_abbr': 'mia',
                 'home_score': 28,
                 'winning_name': 'Buffalo Bills',
                 'winning_abbr': 'buf',
                 'losing_name': 'Miami Dolphins',
                 'losing_abbr': 'mia'},
                {'boxscore': '202009200gnb',
                 'away_name': 'Detroit Lions',
                 'away_abbr': 'det',
                 'away_score': 21,
                 'home_name': 'Green Bay Packers',
                 'home_abbr': 'gnb',
                 'home_score': 42,
                 'winning_name': 'Green Bay Packers',
                 'winning_abbr': 'gnb',
                 'losing_name': 'Detroit Lions',
                 'losing_abbr': 'det'},
                {'boxscore': '202009200dal',
                 'away_name': 'Atlanta Falcons',
                 'away_abbr': 'atl',
                 'away_score': 39,
                 'home_name': 'Dallas Cowboys',
                 'home_abbr': 'dal',
                 'home_score': 40,
                 'winning_name': 'Dallas Cowboys',
                 'winning_abbr': 'dal',
                 'losing_name': 'Atlanta Falcons',
                 'losing_abbr': 'atl'},
                {'boxscore': '202009200crd',
                 'away_name': 'Washington Football Team',
                 'away_abbr': 'was',
                 'away_score': 15,
                 'home_name': 'Arizona Cardinals',
                 'home_abbr': 'crd',
                 'home_score': 30,
                 'winning_name': 'Arizona Cardinals',
                 'winning_abbr': 'crd',
                 'losing_name': 'Washington Football Team',
                 'losing_abbr': 'was'},
                {'boxscore': '202009200sdg',
                 'away_name': 'Kansas City Chiefs',
                 'away_abbr': 'kan',
                 'away_score': 23,
                 'home_name': 'Los Angeles Chargers',
                 'home_abbr': 'sdg',
                 'home_score': 20,
                 'winning_name': 'Kansas City Chiefs',
                 'winning_abbr': 'kan',
                 'losing_name': 'Los Angeles Chargers',
                 'losing_abbr': 'sdg'},
                {'boxscore': '202009200htx',
                 'away_name': 'Baltimore Ravens',
                 'away_abbr': 'rav',
                 'away_score': 33,
                 'home_name': 'Houston Texans',
                 'home_abbr': 'htx',
                 'home_score': 16,
                 'winning_name': 'Baltimore Ravens',
                 'winning_abbr': 'rav',
                 'losing_name': 'Houston Texans',
                 'losing_abbr': 'htx'},
                {'boxscore': '202009200sea',
                 'away_name': 'New England Patriots',
                 'away_abbr': 'nwe',
                 'away_score': 30,
                 'home_name': 'Seattle Seahawks',
                 'home_abbr': 'sea',
                 'home_score': 35,
                 'winning_name': 'Seattle Seahawks',
                 'winning_abbr': 'sea',
                 'losing_name': 'New England Patriots',
                 'losing_abbr': 'nwe'},
                {'boxscore': '202009210rai',
                 'away_name': 'New Orleans Saints',
                 'away_abbr': 'nor',
                 'away_score': 24,
                 'home_name': 'Las Vegas Raiders',
                 'home_abbr': 'rai',
                 'home_score': 34,
                 'winning_name': 'Las Vegas Raiders',
                 'winning_abbr': 'rai',
                 'losing_name': 'New Orleans Saints',
                 'losing_abbr': 'nor'}
            ]
        }
        result = Boxscores(1, 2020, 2).games

        assert result == expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(1, 2020)

        assert result.__repr__() == 'NFL games for week 1'

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation_multi_week(self, *args,
                                                               **kwargs):
        result = Boxscores(1, 2020, 2)

        assert result.__repr__() == 'NFL games for weeks 1, 2'
