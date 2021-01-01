import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import NEUTRAL, REGULAR_SEASON, WIN
from sportsipy.ncaab.boxscore import Boxscore
from sportsipy.ncaab.constants import SCHEDULE_URL
from sportsipy.ncaab.schedule import Schedule


MONTH = 11
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 39


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html')

    schedule = read_file('%s-schedule.html' % (YEAR + 1))
    return MockPQ(schedule)


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


class TestNCAABSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'boxscore_index': '2017-11-14-21-kansas',
            'date': 'Tue, Nov 14, 2017',
            'time': '9:30 pm/est',
            'datetime': datetime(2017, 11, 14, 21, 30),
            'type': REGULAR_SEASON,
            'location': NEUTRAL,
            'opponent_abbr': 'kentucky',
            'opponent_name': 'Kentucky',
            'opponent_rank': 7,
            'opponent_conference': 'SEC',
            'result': WIN,
            'points_for': 65,
            'points_against': 61,
            'overtimes': 0,
            'season_wins': 2,
            'season_losses': 0,
            'streak': 'W 2',
            'arena': 'United Center'
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        self.schedule = Schedule('KANSAS')

    def test_ncaab_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_ncaab_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_ncaab_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2017, 11, 14))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_ncaab_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['KANSAS'])

        match_two = self.schedule[1]
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, match_two.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_ncaab_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_ncaab_schedule_all_dataframe_returns_dataframe(self):

        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_ncaab_schedule_all_dataframe_extended_returns_dataframe(self):
        result = self.schedule.dataframe_extended

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        with pytest.raises(ValueError):
            self.schedule(datetime.now())

    def test_empty_page_return_no_games(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        schedule = Schedule('KANSAS')

        assert len(schedule) == 0

    def test_game_string_representation(self):
        game = self.schedule[0]

        assert game.__repr__() == 'Fri, Nov 10, 2017 - tennessee-state'

    def test_schedule_string_representation(self):
        expected = """Fri, Nov 10, 2017 - tennessee-state
Tue, Nov 14, 2017 - kentucky
Fri, Nov 17, 2017 - south-dakota-state
Tue, Nov 21, 2017 - texas-southern
Fri, Nov 24, 2017 - oakland
Tue, Nov 28, 2017 - toledo
Sat, Dec 2, 2017 - syracuse
Wed, Dec 6, 2017 - washington
Sun, Dec 10, 2017 - arizona-state
Sat, Dec 16, 2017 - nebraska
Mon, Dec 18, 2017 - nebraska-omaha
Thu, Dec 21, 2017 - stanford
Fri, Dec 29, 2017 - texas
Tue, Jan 2, 2018 - texas-tech
Sat, Jan 6, 2018 - texas-christian
Tue, Jan 9, 2018 - iowa-state
Sat, Jan 13, 2018 - kansas-state
Mon, Jan 15, 2018 - west-virginia
Sat, Jan 20, 2018 - baylor
Tue, Jan 23, 2018 - oklahoma
Sat, Jan 27, 2018 - texas-am
Mon, Jan 29, 2018 - kansas-state
Sat, Feb 3, 2018 - oklahoma-state
Tue, Feb 6, 2018 - texas-christian
Sat, Feb 10, 2018 - baylor
Tue, Feb 13, 2018 - iowa-state
Sat, Feb 17, 2018 - west-virginia
Mon, Feb 19, 2018 - oklahoma
Sat, Feb 24, 2018 - texas-tech
Mon, Feb 26, 2018 - texas
Sat, Mar 3, 2018 - oklahoma-state
Thu, Mar 8, 2018 - oklahoma-state
Fri, Mar 9, 2018 - kansas-state
Sat, Mar 10, 2018 - west-virginia
Thu, Mar 15, 2018 - pennsylvania
Sat, Mar 17, 2018 - seton-hall
Fri, Mar 23, 2018 - clemson
Sun, Mar 25, 2018 - duke
Sat, Mar 31, 2018 - villanova"""

        assert self.schedule.__repr__() == expected


class TestNCAABScheduleInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        results = {
            'game': 2,
            'boxscore_index': '2017-11-14-21-kansas',
            'date': 'Tue, Nov 14, 2017',
            'time': '9:30 pm/est',
            'datetime': datetime(2017, 11, 14, 21, 30),
            'type': REGULAR_SEASON,
            'location': NEUTRAL,
            'opponent_abbr': 'kentucky',
            'opponent_name': 'Kentucky',
            'opponent_rank': 7,
            'opponent_conference': 'SEC',
            'result': WIN,
            'points_for': 65,
            'points_against': 61,
            'overtimes': 0,
            'season_wins': 2,
            'season_losses': 0,
            'streak': 'W 2',
            'arena': 'United Center'
        }
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        schedule = Schedule('KANSAS')

        for attribute, value in results.items():
            assert getattr(schedule[1], attribute) == value
