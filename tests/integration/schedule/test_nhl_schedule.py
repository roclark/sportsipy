import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, LOSS
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
