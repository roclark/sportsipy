import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from mock import patch
from os import path
from pyquery import PyQuery as pq
from sportsipy import utils
from sportsipy.constants import AWAY, DRAW
from sportsipy.fb.schedule import Schedule


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
            'expected_goals': 0.3,
            'expected_goals_against': 2.9,
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
            self.schedule(datetime(2020, 7, 1))

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

    def test_no_captain_returns_default(self):
        table_item = '<td data-stat="captain"><a></a></td>'

        captain = self.schedule[0]._parse_captain_id(pq(table_item))

        assert not captain

    def test_no_match_report_returns_default(self):
        table_item = '<td data-stat="match_report"><a></a></td>'

        report = self.schedule[0]._parse_match_report(pq(table_item))

        assert not report

    def test_fb_schedule_string_representation(self):
        expected = """2019-08-10 - Aston Villa
2019-08-17 - Manchester City
2019-08-25 - Newcastle Utd
2019-09-01 - Arsenal
2019-09-14 - Crystal Palace
2019-09-18 - gr Olympiacos
2019-09-21 - Leicester City
2019-09-24 - Colchester Utd
2019-09-28 - Southampton
2019-10-01 - de Bayern Munich
2019-10-05 - Brighton
2019-10-19 - Watford
2019-10-22 - rs Red Star
2019-10-27 - Liverpool
2019-11-03 - Everton
2019-11-06 - rs Red Star
2019-11-09 - Sheffield Utd
2019-11-23 - West Ham
2019-11-26 - gr Olympiacos
2019-11-30 - Bournemouth
2019-12-04 - Manchester Utd
2019-12-07 - Burnley
2019-12-11 - de Bayern Munich
2019-12-15 - Wolves
2019-12-22 - Chelsea
2019-12-26 - Brighton
2019-12-28 - Norwich City
2020-01-01 - Southampton
2020-01-05 - Middlesbrough
2020-01-11 - Liverpool
2020-01-14 - Middlesbrough
2020-01-18 - Watford
2020-01-22 - Norwich City
2020-01-25 - Southampton
2020-02-02 - Manchester City
2020-02-05 - Southampton
2020-02-16 - Aston Villa
2020-02-19 - de RB Leipzig
2020-02-22 - Chelsea
2020-03-01 - Wolves
2020-03-04 - Norwich City
2020-03-07 - Burnley
2020-03-10 - de RB Leipzig
2020-06-19 - Manchester Utd
2020-06-23 - West Ham
2020-07-02 - Sheffield Utd
2020-07-06 - Everton
2020-07-09 - Bournemouth
2020-07-12 - Arsenal
2020-07-15 - Newcastle Utd
2020-07-19 - Leicester City
2020-07-26 - Crystal Palace"""

        assert self.schedule.__repr__() == expected

    def test_fb_game_string_representation(self):
        game = self.schedule[0]

        assert game.__repr__() == '2019-08-10 - Aston Villa'
