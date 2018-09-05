import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, LOSS
from sportsreference.nhl.boxscore import Boxscore
from sportsreference.nhl.constants import SCHEDULE_URL
from sportsreference.nhl.schedule import Schedule


MONTH = 1
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 82


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html')

    schedule = read_file('%s_gamelog.html' % YEAR)
    return MockPQ(schedule)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNHLSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'boxscore_index': '201610150STL',
            'date': '2016-10-15',
            'datetime': datetime(2016, 10, 15),
            'location': AWAY,
            'opponent_abbr': 'STL',
            'opponent_name': 'St. Louis Blues',
            'goals_scored': 2,
            'goals_allowed': 3,
            'result': LOSS,
            'overtime': 0,
            'shots_on_goal': 35,
            'penalties_in_minutes': 8,
            'power_play_goals': 0,
            'power_play_opportunities': 2,
            'short_handed_goals': 0,
            'opp_shots_on_goal': 18,
            'opp_penalties_in_minutes': 4,
            'opp_power_play_goals': 1,
            'opp_power_play_opportunities': 5,
            'opp_short_handed_goals': 0,
            'corsi_for': 54,
            'corsi_against': 23,
            'corsi_for_percentage': 70.1,
            'fenwick_for': 41,
            'fenwick_against': 18,
            'fenwick_for_percentage': 69.5,
            'faceoff_wins': 29,
            'faceoff_losses': 18,
            'faceoff_win_percentage': 61.7,
            'offensive_zone_start_percentage': 55.2,
            'pdo': 92.4
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('NYR')

    def test_nhl_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nhl_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nhl_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2016, 10, 15))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nhl_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['NYR'])

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

    def test_nhl_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nhl_schedule_all_dataframe_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))
        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nhl_schedule_all_dataframe_extended_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule.dataframe_extended

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        with pytest.raises(ValueError):
            self.schedule(datetime.now())
