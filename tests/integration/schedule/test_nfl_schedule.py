import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, REGULAR_SEASON, WIN
from sportsreference.nfl.boxscore import Boxscore
from sportsreference.nfl.constants import SCHEDULE_URL
from sportsreference.nfl.schedule import Schedule


MONTH = 9
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 19


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if 'playoff' in div.lower():
                return read_file('playoff_table.html')
            return read_file('table.html')

    schedule = read_file('gamelog')
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


class TestNFLSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'week': 2,
            'boxscore_index': '201709170nor',
            'day': 'Sun',
            'date': 'September 17',
            'type': REGULAR_SEASON,
            'datetime': datetime(2017, 9, 17, 0, 0),
            'result': WIN,
            'overtime': 0,
            'location': AWAY,
            'opponent_abbr': 'NOR',
            'opponent_name': 'New Orleans Saints',
            'points_scored': 36,
            'points_allowed': 20,
            'pass_completions': 30,
            'pass_attempts': 39,
            'pass_yards': 436,
            'pass_touchdowns': 3,
            'interceptions': 0,
            'times_sacked': 2,
            'yards_lost_from_sacks': 11,
            'pass_yards_per_attempt': 11.2,
            'pass_completion_rate': 76.9,
            'quarterback_rating': 138.4,
            'rush_attempts': 31,
            'rush_yards': 119,
            'rush_yards_per_attempt': 3.8,
            'rush_touchdowns': 1,
            'field_goals_made': 3,
            'field_goals_attempted': 3,
            'extra_points_made': 3,
            'extra_points_attempted': 4,
            'punts': 3,
            'punt_yards': 111,
            'third_down_conversions': 6,
            'third_down_attempts': 12,
            'fourth_down_conversions': 0,
            'fourth_down_attempts': 0,
            'time_of_possession': '35:06'
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

        self.schedule = Schedule('NWE')

    def test_nfl_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nfl_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nfl_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2017, 9, 17))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nfl_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['NWE'])

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

    def test_nfl_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nfl_schedule_all_dataframe_returns_dataframe(self):
        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nfl_schedule_all_dataframe_extended_returns_dataframe(self):
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

        schedule = Schedule('NWE')

        assert len(schedule) == 0


class TestNFLScheduleInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        results = {
            'week': 2,
            'boxscore_index': '201709170nor',
            'day': 'Sun',
            'date': 'September 17',
            'type': REGULAR_SEASON,
            'datetime': datetime(2017, 9, 17, 0, 0),
            'result': WIN,
            'overtime': 0,
            'location': AWAY,
            'opponent_abbr': 'NOR',
            'opponent_name': 'New Orleans Saints',
            'points_scored': 36,
            'points_allowed': 20,
            'pass_completions': 30,
            'pass_attempts': 39,
            'pass_yards': 436,
            'pass_touchdowns': 3,
            'interceptions': 0,
            'times_sacked': 2,
            'yards_lost_from_sacks': 11,
            'pass_yards_per_attempt': 11.2,
            'pass_completion_rate': 76.9,
            'quarterback_rating': 138.4,
            'rush_attempts': 31,
            'rush_yards': 119,
            'rush_yards_per_attempt': 3.8,
            'rush_touchdowns': 1,
            'field_goals_made': 3,
            'field_goals_attempted': 3,
            'extra_points_made': 3,
            'extra_points_attempted': 4,
            'punts': 3,
            'punt_yards': 111,
            'third_down_conversions': 6,
            'third_down_attempts': 12,
            'fourth_down_conversions': 0,
            'fourth_down_attempts': 0,
            'time_of_possession': '35:06'
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

        schedule = Schedule('NWE')

        for attribute, value in results.items():
            assert getattr(schedule[1], attribute) == value
