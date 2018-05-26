import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import HOME, REGULAR_SEASON, WIN
from sportsreference.ncaaf.constants import SCHEDULE_URL
from sportsreference.ncaaf.schedule import Schedule


MONTH = 9
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 13


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaaf', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html' % YEAR)

    schedule = read_file('%s-schedule.html' % YEAR)
    return MockPQ(schedule)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAAFSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'date': 'Sep 9, 2017',
            'time': '12:00 PM',
            'day_of_week': 'Sat',
            'datetime': datetime(2017, 9, 9, 12, 0),
            'location': HOME,
            'rank': 8,
            'opponent_abbr': 'cincinnati',
            'opponent_name': 'Cincinnati',
            'opponent_rank': None,
            'opponent_conference': 'American',
            'result': WIN,
            'points_for': 36,
            'points_against': 14,
            'wins': 2,
            'losses': 0,
            'streak': 'W 2'
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('MICHIGAN')

    def test_ncaaf_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_ncaaf_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_ncaaf_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2017, 9, 9))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value
