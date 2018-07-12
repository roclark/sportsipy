import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME, LOSS, WIN
from sportsreference.mlb.constants import DAY, NIGHT, SCHEDULE_URL
from sportsreference.mlb.schedule import Schedule


MONTH = 4
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 162


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html')

    schedule = read_file('%s-schedule-scores.html' % YEAR)
    return MockPQ(schedule)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestMLBSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'date': 'Tuesday, Apr 4',
            'datetime': datetime(2017, 4, 4),
            'game_number_for_day': 1,
            'location': AWAY,
            'opponent_abbr': 'TBR',
            'result': WIN,
            'runs_scored': 5,
            'runs_allowed': 0,
            'innings': 9,
            'record': '1-1',
            'rank': 3,
            'games_behind': 0.5,
            'winner': 'Sabathia',
            'loser': 'Odorizzi',
            'save': None,
            'game_duration': '3:07',
            'day_or_night': NIGHT,
            'attendance': 19366,
            'streak': '+'
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('NYY')

    def test_mlb_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_mlb_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_mlb_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2017, 4, 4))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_mlb_schedule_returns_second_game_in_double_header(self):
        match_two = self.schedule(datetime(2017, 5, 14), 2)
        results = {
            'game': 35,
            'date': 'Sunday, May 14 (2)',
            'datetime': datetime(2017, 5, 14),
            'game_number_for_day': 2,
            'location': HOME,
            'opponent_abbr': 'HOU',
            'result': LOSS,
            'runs_scored': 7,
            'runs_allowed': 10,
            'innings': 9,
            'record': '22-13',
            'rank': 1,
            'games_behind': -0.5,
            'winner': 'Morton',
            'loser': 'Tanaka',
            'save': None,
            'game_duration': '3:49',
            'day_or_night': NIGHT,
            'attendance': 47883,
            'streak': '-'
        }

        for attribute, value in results.items():
            assert getattr(match_two, attribute) == value
