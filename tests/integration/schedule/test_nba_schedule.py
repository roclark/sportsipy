import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY, WIN
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
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('PHO')

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
