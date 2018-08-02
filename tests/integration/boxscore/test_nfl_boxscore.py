import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.nfl.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsreference.nfl.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2017

BOXSCORE = '201802040nwe'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (YEAR, 7):
        return MockPQ(read_file('boxscores.html'))
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
            'date': 'Sunday Feb 4, 2018',
            'time': '6:30pm',
            'stadium': 'U.S. Bank Stadium',
            'attendance': 67612,
            'duration': '3:46',
            'winner': AWAY,
            'winning_name': 'Philadelphia Eagles',
            'winning_abbr': 'PHI',
            'losing_name': 'New England Patriots',
            'losing_abbr': 'NWE',
            'away_points': 41,
            'away_first_downs': 25,
            'away_rush_attempts': 27,
            'away_rush_yards': 164,
            'away_rush_touchdowns': 1,
            'away_pass_completions': 29,
            'away_pass_attempts': 44,
            'away_pass_yards': 374,
            'away_pass_touchdowns': 4,
            'away_interceptions': 1,
            'away_times_sacked': 0,
            'away_yards_lost_from_sacks': 0,
            'away_net_pass_yards': 374,
            'away_total_yards': 538,
            'away_fumbles': 0,
            'away_fumbles_lost': 0,
            'away_turnovers': 1,
            'away_penalties': 6,
            'away_yards_from_penalties': 35,
            'away_third_down_conversions': 10,
            'away_third_down_attempts': 16,
            'away_fourth_down_conversions': 2,
            'away_fourth_down_attempts': 2,
            'away_time_of_possession': '34:04',
            'home_points': 33,
            'home_first_downs': 29,
            'home_rush_attempts': 22,
            'home_rush_yards': 113,
            'home_rush_touchdowns': 1,
            'home_pass_completions': 28,
            'home_pass_attempts': 49,
            'home_pass_yards': 505,
            'home_pass_touchdowns': 3,
            'home_interceptions': 0,
            'home_times_sacked': 1,
            'home_yards_lost_from_sacks': 5,
            'home_net_pass_yards': 500,
            'home_total_yards': 613,
            'home_fumbles': 1,
            'home_fumbles_lost': 1,
            'home_turnovers': 1,
            'home_penalties': 1,
            'home_yards_from_penalties': 5,
            'home_third_down_conversions': 5,
            'home_third_down_attempts': 10,
            'home_fourth_down_conversions': 1,
            'home_fourth_down_attempts': 2,
            'home_time_of_possession': '25:56',
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nfl_boxscore_returns_requested_boxscore(self):
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


class TestNFLBoxscores:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        expected = {
            'boxscores': [
                {'home_name': 'Oakland Raiders',
                 'home_abbr': 'rai',
                 'boxscore': '201710190rai',
                 'away_name': 'Kansas City Chiefs',
                 'away_abbr': 'kan'},
                {'home_name': 'Chicago Bears',
                 'home_abbr': 'chi',
                 'boxscore': '201710220chi',
                 'away_name': 'Carolina Panthers',
                 'away_abbr': 'car'},
                {'home_name': 'Buffalo Bills',
                 'home_abbr': 'buf',
                 'boxscore': '201710220buf',
                 'away_name': 'Tampa Bay Buccaneers',
                 'away_abbr': 'tam'},
                {'home_name': 'Los Angeles Rams',
                 'home_abbr': 'ram',
                 'boxscore': '201710220ram',
                 'away_name': 'Arizona Cardinals',
                 'away_abbr': 'crd'},
                {'home_name': 'Minnesota Vikings',
                 'home_abbr': 'min',
                 'boxscore': '201710220min',
                 'away_name': 'Baltimore Ravens',
                 'away_abbr': 'rav'},
                {'home_name': 'Miami Dolphins',
                 'home_abbr': 'mia',
                 'boxscore': '201710220mia',
                 'away_name': 'New York Jets',
                 'away_abbr': 'nyj'},
                {'home_name': 'Green Bay Packers',
                 'home_abbr': 'gnb',
                 'boxscore': '201710220gnb',
                 'away_name': 'New Orleans Saints',
                 'away_abbr': 'nor'},
                {'home_name': 'Indianapolis Colts',
                 'home_abbr': 'clt',
                 'boxscore': '201710220clt',
                 'away_name': 'Jacksonville Jaguars',
                 'away_abbr': 'jax'},
                {'home_name': 'Cleveland Browns',
                 'home_abbr': 'cle',
                 'boxscore': '201710220cle',
                 'away_name': 'Tennessee Titans',
                 'away_abbr': 'oti'},
                {'home_name': 'San Francisco 49ers',
                 'home_abbr': 'sfo',
                 'boxscore': '201710220sfo',
                 'away_name': 'Dallas Cowboys',
                 'away_abbr': 'dal'},
                {'home_name': 'Los Angeles Chargers',
                 'home_abbr': 'sdg',
                 'boxscore': '201710220sdg',
                 'away_name': 'Denver Broncos',
                 'away_abbr': 'den'},
                {'home_name': 'Pittsburgh Steelers',
                 'home_abbr': 'pit',
                 'boxscore': '201710220pit',
                 'away_name': 'Cincinnati Bengals',
                 'away_abbr': 'cin'},
                {'home_name': 'New York Giants',
                 'home_abbr': 'nyg',
                 'boxscore': '201710220nyg',
                 'away_name': 'Seattle Seahawks',
                 'away_abbr': 'sea'},
                {'home_name': 'New England Patriots',
                 'home_abbr': 'nwe',
                 'boxscore': '201710220nwe',
                 'away_name': 'Atlanta Falcons',
                 'away_abbr': 'atl'},
                {'home_name': 'Philadelphia Eagles',
                 'home_abbr': 'phi',
                 'boxscore': '201710230phi',
                 'away_name': 'Washington Redskins',
                 'away_abbr': 'was'},
            ]
        }

        result = Boxscores(7, 2017).games

        assert result == expected
