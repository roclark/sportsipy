import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.ncaaf.constants import BOXSCORE_URL
from sportsreference.ncaaf.boxscore import Boxscore


MONTH = 10
YEAR = 2017

BOXSCORE = '2018-01-08-georgia'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaaf', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAAFBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Monday Jan 8, 2018',
            'time': '8:00 PM ET',
            'stadium': 'Mercedes-Benz Stadium - Atlanta, Georgia',
            'winner': AWAY,
            'winning_name': 'Alabama',
            'winning_abbr': 'ALABAMA',
            'losing_name': 'Georgia',
            'losing_abbr': 'GEORGIA',
            'away_points': 26,
            'away_first_downs': 20,
            'away_rush_attempts': 39,
            'away_rush_yards': 184,
            'away_rush_touchdowns': 0,
            'away_pass_completions': 17,
            'away_pass_attempts': 32,
            'away_pass_yards': 187,
            'away_pass_touchdowns': 3,
            'away_interceptions': 1,
            'away_total_yards': 371,
            'away_fumbles': 0,
            'away_fumbles_lost': 0,
            'away_turnovers': 1,
            'away_penalties': 6,
            'away_yards_from_penalties': 41,
            'home_points': 23,
            'home_first_downs': 22,
            'home_rush_attempts': 45,
            'home_rush_yards': 133,
            'home_rush_touchdowns': 1,
            'home_pass_completions': 16,
            'home_pass_attempts': 32,
            'home_pass_yards': 232,
            'home_pass_touchdowns': 1,
            'home_interceptions': 2,
            'home_total_yards': 365,
            'home_fumbles': 0,
            'home_fumbles_lost': 0,
            'home_turnovers': 2,
            'home_penalties': 6,
            'home_yards_from_penalties': 65
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_ncaaf_boxscore_returns_requested_boxscore(self):
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

    def test_ncaaf_boxscore_dataframe_returns_dataframe_of_all_values(self):
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
