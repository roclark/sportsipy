import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from mock import patch
from os import path
from sportsreference import utils
from sportsreference.constants import AWAY, DRAW
from sportsreference.fb.schedule import Schedule


NUM_GAMES_IN_SCHEDULE = 52


def read_file(filename):
    filepath = path.join(path.dirname(__file__), 'fb_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    contents = read_file('tottenham-hotspur-2019-2020.html')
    return MockPQ(contents)


class TestFBSchedule:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'competition': 'Premier League',
            'matchweek': 'Matchweek 2',
            'day': 'Sat',
            'date': '2019-08-17',
            'time': '17:30',
            'datetime': datetime(2019, 8, 17, 17, 30),
            'venue': AWAY,
            'result': DRAW,
            'goals_for': 2,
            'goals_against': 2,
            'shootout_scored': None,
            'shootout_against': None,
            'opponent': 'Manchester City',
            'opponent_id': 'b8fd03ef',
            'expected_goals': 0.2,
            'expected_goals_against': 3.0,
            'attendance': 54503,
            'captain': 'Hugo Lloris',
            'captain_id': '8f62b6ee',
            'formation': '4-2-3-1',
            'referee': 'Michael Oliver',
            'match_report': 'a4ba771e',
            'notes': ''
        }

        self.schedule = Schedule('Tottenham Hotspur')

    def test_fb_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_fb_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_fb_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2019, 8, 17))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

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

        schedule = Schedule('Tottenham Hotspur')

        assert len(schedule) == 0

    def test_schedule_iter_returns_correct_number_of_games(self):
        for count, _ in enumerate(self.schedule):
            pass

        assert count + 1 == NUM_GAMES_IN_SCHEDULE

    def test_fb_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['a4ba771e'])

        match_two = self.schedule[1]
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected on above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, match_two.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty
