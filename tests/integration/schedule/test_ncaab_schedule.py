import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import NEUTRAL, REGULAR_SEASON, WIN
from sportsreference.ncaab.boxscore import Boxscore
from sportsreference.ncaab.constants import SCHEDULE_URL
from sportsreference.ncaab.schedule import Schedule


MONTH = 11
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 39


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab', filename)
    return open('%s' % filepath, 'r').read()


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

        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_ncaab_schedule_all_dataframe_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_ncaab_schedule_all_dataframe_extended_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule.dataframe_extended

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        with pytest.raises(ValueError):
            self.schedule(datetime.now())
