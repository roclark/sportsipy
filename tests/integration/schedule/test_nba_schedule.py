import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, WIN
from sportsreference.nba.boxscore import Boxscore
from sportsreference.nba.constants import SCHEDULE_URL
from sportsreference.nba.schedule import Schedule


MONTH = 1
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 99


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if 'playoff' in div:
                return read_file('playoff.html')
            return read_file('table.html')

    schedule = read_file('gamelog')
    return MockPQ(schedule)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNBASchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'boxscore_index': '201610280NOP',
            'date': '2016-10-28',
            'datetime': datetime(2016, 10, 28),
            'location': AWAY,
            'opponent_abbr': 'NOP',
            'result': WIN,
            'points_scored': 122,
            'points_allowed': 114,
            'field_goals': 44,
            'field_goal_attempts': 91,
            'field_goal_percentage': .484,
            'three_point_field_goals': 9,
            'three_point_field_goal_attempts': 28,
            'three_point_field_goal_percentage': .321,
            'free_throws': 25,
            'free_throw_attempts': 28,
            'free_throw_percentage': .893,
            'offensive_rebounds': 9,
            'total_rebounds': 49,
            'assists': 32,
            'steals': 8,
            'blocks': 2,
            'turnovers': 14,
            'personal_fouls': 22,
            'opp_field_goals': 47,
            'opp_field_goal_attempts': 100,
            'opp_field_goal_percentage': .470,
            'opp_three_point_field_goals': 5,
            'opp_three_point_field_goal_attempts': 22,
            'opp_three_point_field_goal_percentage': .227,
            'opp_free_throws': 15,
            'opp_free_throw_attempts': 23,
            'opp_free_throw_percentage': .652,
            'opp_offensive_rebounds': 12,
            'opp_total_rebounds': 49,
            'opp_assists': 29,
            'opp_steals': 8,
            'opp_blocks': 5,
            'opp_turnovers': 13,
            'opp_personal_fouls': 24
        }
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('GSW')

    def test_nba_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nba_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nba_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2016, 10, 28))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nba_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['PHO'])

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

    def test_nba_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nba_schedule_all_dataframe_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))
        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nba_schedule_all_dataframe_extended_returns_dataframe(self):
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        result = self.schedule.dataframe_extended

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        with pytest.raises(ValueError):
            self.schedule(datetime.now())
